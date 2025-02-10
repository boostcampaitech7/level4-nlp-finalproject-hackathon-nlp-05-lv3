import torch
import pandas as pd
from datasets import Dataset
from peft import get_peft_model, LoraConfig, TaskType
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainerCallback, TrainingArguments, Trainer


class Review_DeepSeekTrainer:
    def __init__(self, model_path, train_path, eval_path, output_dir):
        self.model_path = model_path
        self.train_path = train_path,
        self.eval_path = eval_path
        self.output_dir = output_dir
        self.PROMPT = """당신은 식품 리뷰의 감성 분석 및 평가 전문가입니다. 주어진 식품 리뷰를 분석하여 해당 리뷰에서 속성과 평가, 감성을 추출하세요.

### 작업 목표:
1. 입력으로 주어지는 식품 리뷰를 분석하여 JSON 형식으로 출력하세요.
2. JSON 형식은 아래와 같이 리스트 형태로 구성됩니다.
    ```json
    [
        {{"속성": "<속성명1>", "평가": "<평가 내용1>", "감정": "<긍정/부정/중립>"}},
        {{"속성": "<속성명2>", "평가": "<평가 내용2>", "감정": "<긍정/부정/중립>"}},
        ...
    ]
    ```

속성은 다음 중 하나일 가능성이 높습니다: ["상품", "배송", "가격", "맛", "신선도", "양", "포장"].
만약 새로운 속성이 필요하면 생성하여 사용 가능합니다.
모든 식품명은 "상품"으로 통일합니다.

### 세부 규칙:
- 감정 분석
    - 리뷰에서 감정이 긍정적인 경우 "감정": "긍정"으로 설정합니다.
    - 부정적인 표현이 포함된 경우 "감정": "부정"으로 설정합니다.
    - 평가가 모호하거나 가정적인 경우 "감정": "중립"으로 설정합니다.

- 평가 문구 정제
    - 리뷰에서 나타난 주요 평가를 간결한 문장으로 변환합니다.
    - 핵심 키워드를 유지하면서 불필요한 표현은 제거합니다.
    - 평가 문구는 '~다.'로 끝나는 현재형, 평서문으로 답변합니다. 예를 들어, '좋습니다.' 가 아닌 '좋다.' 로 작성합니다.

- 예외 사항
    - 상품 사용 후기가 아닌 상품에 대한 예상이나 기대하는 부분은 분리하여 제외합니다.
    - 복합적인 평가가 존재하는 경우 해당 내용을 분리하여 각각 JSON 항목으로 작성합니다. 예를 들어, '배송이 안전하고 빨랐어요'의 경우 '안전하다.' 와 '빠르다.' 두 가지로 구분합니다.

### 입력:
{review}
"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = self.load_model()

    def load_model(self):
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float32
        )

        model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            quantization_config=bnb_config,
            device_map="auto"
        )

        lora_config = LoraConfig(
            target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
            r=8,
            lora_alpha=16,
            lora_dropout=0.1,
            task_type=TaskType.CAUSAL_LM
        )

        return get_peft_model(model, lora_config)
    
    def load_datasets(self):
        train_data_df = pd.read_csv(self.train_path)
        eval_data_df = pd.read_csv(self.eval_path)

        train_dataset = [{"prompt": self.PROMPT.format(review=txt), "completion": think} 
                         for txt, think in zip(train_data_df["processed"], train_data_df["GPT-4o-Response"])]
        eval_dataset = [{"prompt": self.PROMPT.format(review=txt), "completion": answer} 
                         for txt, answer in zip(eval_data_df["processed"], eval_data_df["GPT-4o-Response"])]
        
        return Dataset.from_list(train_dataset), Dataset.from_list(eval_dataset)

    def tokenize_func(self, dataset):
        combined_texts = [f"{prompt}\n{completion}" for prompt, completion in zip(dataset["prompt"], dataset["completion"])]
        tokenized = self.tokenizer(combined_texts, truncation=True, max_length=800, padding="max_length")
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized
    
    def train(self):
        tokenized_train_dataset = self.train_datset.map(self.tokenize_func, batched=True)
        tokenized_eval_dataset = self.eval_datset.map(self.tokenize_func, batched=True)

        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=5,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=16,
            fp16=True,
            logging_steps=10,
            save_steps=100,
            per_device_eval_batch_size=1,
            evaluation_strategy="steps",
            eval_strategy="steps",
            eval_steps=10,
            learning_rate=1e-5,
            logging_dir="./logs",
            run_name=self.output_dir,
        )

        class MoveToCPUTensorCallback(TrainerCallback):
            def on_step_end(self, args, state, control, **kwargs):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_train_dataset,
            eval_dataset=tokenized_eval_dataset,
            callbacks=[MoveToCPUTensorCallback()]
        )

        trainer.train()

        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        print(f"Model saved to {self.output_dir}")

if __name__ == "__main__":
    trainer = Review_DeepSeekTrainer(
        model_path="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        train_path="./data/aste/train/train_data.csv",
        eval_path="./data/aste/eval/aste_annotation_100_golden_label.csv",
        output_dir="./deepseek_14b_finetune"
    )
