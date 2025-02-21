import argparse
import yaml
import os
import urllib.request
import logging
from io import BytesIO
from PIL import Image
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    TrainerCallback
)
from datasets import load_dataset
from dataclasses import dataclass
from typing import Any, Dict
from janus.models import VLChatProcessor, MultiModalityCausalLM
from janus.utils.io import load_pil_images

# Trainer 콜백: GPU 메모리 해제
class MoveToCPUTensorCallback(TrainerCallback):
    def on_step_end(self, args, state, control, **kwargs):
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

def main():
    # argparse를 통해 config 파일 경로를 입력받음
    parser = argparse.ArgumentParser(description="Janus-Pro 7B 파인튜닝 실행")
    parser.add_argument(
        "--config",
        "-c",
        default="config/config.yaml",
        help="설정 파일 경로 (기본값: config/config.yaml)"
    )
    args = parser.parse_args()

    # config.yaml 로드
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # config.yaml의 값을 활용하여 변수 설정
    # 모델명: config에 janus_pro_finetuning 섹션이 있다면 사용, 없으면 기본값 사용
    model_name = config.get("janus_pro_finetuning", {}).get("model_name", "deepseek-ai/Janus-Pro-7B")
    
    # CSV 파일 경로: paths > data_dir와 thumbnail_1347_gpt_human_labeling_train 값을 조합
    data_dir = config.get("paths", {}).get("data_dir", "./data")
    csv_file = config.get("paths", {}).get("thumbnail_1347_gpt_human_labeling_train", "thumbnail_1347_gpt_human_labeling_train.csv")
    csv_path = os.path.join(data_dir, csv_file)

    # 모델 저장 출력 디렉토리 (config에 별도 설정이 없으면 기본값 사용)
    output_dir = config.get("paths", {}).get("janus_pro_output_dir", "./janus_pro7b_finetuned")

    logging.info(f"모델명: {model_name}")
    logging.info(f"학습 CSV 파일 경로: {csv_path}")
    logging.info(f"출력 디렉토리: {output_dir}")

    # 1. 모델 및 프로세서/토크나이저 로드
    # VLChatProcessor를 사용해 이미지 전처리 및 토크나이저 로드
    vl_chat_processor: VLChatProcessor = VLChatProcessor.from_pretrained(model_name)
    tokenizer = vl_chat_processor.tokenizer

    # 모델 로드 (양자화 없이, FP16 precision 사용)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16
    )

    # 2. CSV 파일로부터 데이터셋 로드

    data_files = {"train": csv_path}
    dataset = load_dataset("csv", data_files=data_files)

    # 3. 전처리 함수 정의
    def preprocess_function(example):
        # 텍스트 프롬프트 구성 (CSV 파일 내 컬럼명에 맞게 수정)
        text_prompt = (
            f"Texture: {example['texture']}. "
            f"Shape: {example['shape']}. "
            f"Color: {example['color']}. "
            f"Transparency: {example['transparency']}. "
            f"Design: {example['design']}."
        )
        
        # 이미지 다운로드 및 전처리
        urllib.request.urlretrieve(example["대표 이미지 URL"], "full_test.jpg")
        img = Image.open("full_test.jpg").convert("RGB")
        target_size = (224, 224)
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        img.save("test.jpg")
        
        # 대화 형식 입력 구성
        conversation = {
            "role": "<|User|>",
            "content": f"<image_placeholder>\n{text_prompt}>",
            "images": ["test.jpg"]
        }
        
        # PIL 이미지 로드
        pil_images = load_pil_images([conversation])
        
        # VLChatProcessor를 사용해 입력 변환
        prepare_inputs = vl_chat_processor(
            conversations=[conversation],
            images=pil_images,
            force_batchify=True
        ).to(model.device)
        
        # 입력 딕셔너리 변환: 텐서형 데이터는 FP16으로 변환
        prepare_inputs_dict = {
            k: (v.to(torch.float16) if isinstance(v, torch.Tensor) and v.is_floating_point() else v)
            for k, v in vars(prepare_inputs).items() if not k.startswith("_")
        }
        
        # 이미지 임베딩 생성
        inputs_embeds = model.prepare_inputs_embeds(**prepare_inputs_dict)
        if not isinstance(inputs_embeds, torch.Tensor):
            inputs_embeds = torch.tensor(inputs_embeds)
        inputs_embeds = inputs_embeds.to(torch.float16)
        
        # 라벨 생성: 텍스트 프롬프트를 토크나이저로 인코딩
        labels = tokenizer(
            text_prompt,
            padding="max_length",
            truncation=True,
            max_length=128,
            return_tensors="pt"
        )["input_ids"].squeeze(0)
        
        return {
            "inputs_embeds": inputs_embeds.squeeze(0),
            "labels": labels
        }

    # 데이터셋에 전처리 함수 적용
    dataset = dataset.map(preprocess_function, batched=False)

    # 4. 데이터 Collator 정의
    @dataclass
    class DataCollatorForVLChat:
        def __call__(self, features: list) -> Dict[str, torch.Tensor]:
            inputs_embeds = []
            labels = []
            for f in features:
                # inputs_embeds 처리
                if isinstance(f["inputs_embeds"], torch.Tensor):
                    inputs_embeds.append(f["inputs_embeds"])
                else:
                    inputs_embeds.append(torch.tensor(f["inputs_embeds"], dtype=torch.float16))
                # labels 처리
                if isinstance(f["labels"], torch.Tensor):
                    labels.append(f["labels"])
                else:
                    labels.append(torch.tensor(f["labels"], dtype=torch.long))
            inputs_embeds_batch = torch.stack(inputs_embeds)
            labels_batch = torch.stack(labels)
            return {
                "inputs_embeds": inputs_embeds_batch,
                "labels": labels_batch
            }

    data_collator = DataCollatorForVLChat()

    # 5. TrainingArguments 설정
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=1,
        per_device_train_batch_size=1,
        learning_rate=5e-5,
        save_steps=80,
        fp16=True,
        logging_steps=100,
        save_total_limit=1,
        gradient_accumulation_steps=4,
        remove_unused_columns=False
    )

    # 6. Trainer 생성 및 학습
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        callbacks=[MoveToCPUTensorCallback()]
    )

    trainer.train()
    trainer.save_model(training_args.output_dir)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    main()