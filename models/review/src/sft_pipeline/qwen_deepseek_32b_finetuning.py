from unsloth import FastLanguageModel


def set_model_size(parameters: str) -> str:
    """모델 크기에 따른 모델 이름을 반환합니다."""
    model_map = {
        "14B": "unsloth/DeepSeek-R1-Distill-Qwen-14B-bnb-4bit",
        "32B": "unsloth/DeepSeek-R1-Distill-Qwen-32B-bnb-4bit"
    }
    if parameters in model_map:
        print(f"Setting model size to {parameters}")
        return model_map[parameters]
    else:
        raise ValueError("Invalid model size. Choose '14B' or '32B'.")

def load_model(model_size: str = "32B"):
    """모델과 토크나이저를 로드합니다."""
    model_name = set_model_size(model_size)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
        temperature=0.6
    )
    FastLanguageModel.for_inference(model)
    return model, tokenizer

PROMPT_TEMPLATE = """당신은 식품 리뷰의 감성 분석 및 평가 전문가입니다. 주어진 식품 리뷰를 분석하여 해당 리뷰에서 속성과 평가, 감성을 추출하세요.

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
<think>
"""

model, tokenizer = load_model("32B")

model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0, # Supports any, but = 0 is optimized
    bias = "none",    # Supports any, but = "none" is optimized
    # [NEW] "unsloth" uses 30% less VRAM, fits 2x larger batch sizes!
    use_gradient_checkpointing = "unsloth", # True or "unsloth" for very long context
    random_state = 3407,
    use_rslora = False,  # We support rank stabilized LoRA
    loftq_config = None, # And LoftQ
)

import json
import re
import pandas as pd
from torch.utils.data import Dataset

EOS_TOKEN = tokenizer.eos_token

class ASTEDataset(Dataset):
    def __init__(self, csv_file, encoding='utf-8'):
        """
        csv_file: CSV 파일 경로
        encoding: CSV 파일 인코딩 (기본값: 'utf-8')
        """
        # CSV 파일을 pandas DataFrame으로 로드
        self.data = pd.read_csv(csv_file, encoding=encoding)
        
        self.data['GPT-4o-Answer'] = self.data['GPT-4o-Answer'].apply(
            lambda x: re.sub(r'""', '"', x)
        )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # DataFrame에서 해당 인덱스의 row를 가져옴
        row = self.data.iloc[idx]

        # 리뷰 텍스트를 prompt 템플릿에 맞게 포맷팅
        prompt_text = row['리뷰']
        prompt = PROMPT_TEMPLATE.format(review=prompt_text)

        label_json_str = row['GPT-4o-Answer']
        try:
            label_obj = json.loads(label_json_str)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 빈 리스트 반환
            label_obj = []

        cot = row["GPT-4o-Reasoning"] + "</think>\n"

        # JSON 블록 형태로 가공하여 출력
        label_text = f'```json\n{json.dumps(label_obj, ensure_ascii=False, indent=4)}\n```'

        text_all = prompt + cot + label_text + EOS_TOKEN
        print(text_all)

        return {
            'instruction': prompt,
            'output': label_text,
            'text': text_all,
        }

from ast import literal_eval

def process_aste_example(example):
    """
    datasets.map()에서 각 배치에 적용될 함수
    입력 example은 dict 형태로, 키는 '리뷰', 'aste_golden_label' 등이고 값은 리스트입니다.
    """
    instructions = []
    outputs = []
    texts = []
    
    # 각 배치의 샘플들을 순회
    for review, cot, aste_label in zip(example['리뷰'], example['GPT-4o-Reasoning'], example['GPT-4o-Answer']):
        prompt_text = review
        prompt = PROMPT_TEMPLATE.format(review=prompt_text)

        # 이중 따옴표 문제 해결 및 JSON 파싱 시도
        try:
            label_obj = json.loads(aste_label)  # JSON 변환 시도
        except json.JSONDecodeError:
            try:
                label_obj = literal_eval(aste_label)
            except Exception:
                label_obj = []  # 변환 실패 시 빈 리스트

        # JSON 문자열을 가공
        label_text = f'```json\n{json.dumps(label_obj, ensure_ascii=False, indent=4)}\n```'
        text_all = prompt + cot + '\n</think>\n' + label_text + EOS_TOKEN

        instructions.append(prompt)
        outputs.append(label_text)
        texts.append(text_all)
        
    
    # 각 키별 리스트를 반환하는 dict로 결과 반환
    return {
        'instruction': instructions,
        'output': outputs,
        'text': texts,
    }

from datasets import load_dataset

dataset = load_dataset("csv", data_files="train_gpt_splitted.csv", split="train")
dataset = dataset.map(process_aste_example, batched=True, ) 

print("---")
print("dataset:", dataset[1])
print("---")
print("dataset[1]['text']:", dataset[1]["text"])

from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = 2048,
    dataset_num_proc = 2,
    packing = False, # Can make training 5x faster for short sequences.
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        num_train_epochs = 3, # Set this for 1 full training run.
        # max_steps = 60,
        learning_rate = 2e-4,
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 42,
        output_dir = "output_zeroshot",
        report_to = "none", # Use this for WandB etc
    ),
)

trainer_stats = trainer.train()
