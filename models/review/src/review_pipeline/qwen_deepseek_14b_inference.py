import time
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
from ast import literal_eval
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from utils.evaluate import evaluate_aste


PROMPT = """당신은 식품 리뷰의 감성 분석 및 평가 전문가입니다. 주어진 식품 리뷰를 분석하여 해당 리뷰에서 속성과 평가, 감성을 추출하세요.

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


def prepare_data(path):
    data_df = pd.read_csv(path)
    return data_df

def extract_aste(model_size, quant_type, data_df, col_name):
    """
    model_size: 14 or 8
    quant_type: 8 or 4
    data_df: DataFrame
    """

    # model_name = f"deepseek-ai/DeepSeek-R1-Distill-Qwen-{model_size}B"
    model_name = "deepseek_14b_custom_eval"

    if not quant_type:
        bnb_config = None
    elif quant_type == 4:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float32
        )
    else:
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True
        )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto"
    )

    total_time = 0
    for idx, row in tqdm(data_df[pd.isna(data_df[col_name])].iterrows()):
        txt = row["processed"]
        # answer = row["aste_golden_label"]

        input_text = PROMPT.format(review=txt)
        print(row["review-ID"], txt)

        start_time = time.time()
        inputs = tokenizer(input_text, return_tensors="pt").to("cuda")
        output = model.generate(**inputs,
                                max_new_tokens=512,
                                temperature=0.6,
                                top_p=0.95,
                                do_sample=True)
        output = tokenizer.decode(output[0])

        try:
            aste = str(literal_eval(output.split("</think>")[1].split("```json")[1].split("```<")[0]))
            # thinking = output.split("<think>")[1].split("</think>")[0]
        except Exception as e:
            aste = np.nan
            # thinking = output.split("<think>")[1]
        
        spent = time.time() - start_time

        # print(f"\nreasoning: \n{thinking}")
        print(f"\naste: {aste}")
        # print(f"\nanswer: {answer}")
        print(f"\n{spent}")
        print("\n=============================================================\n")

        total_time += spent
        data_df.loc[idx, col_name] = aste
        # data_df.loc[idx, "thinking"] = thinking
    
    data_df.to_csv("./data/aste/inference/deepseek_14b_inference.csv", index=False)
    print(f"total time: {total_time / len(data_df)}")


if __name__ == "__main__":
    # data_path = "processed_except_GL.csv" # 
    data_path = "./data/aste/eval/aste_annotation_100_golden_label.csv"
    col_name = "inference"

    data_df = prepare_data(data_path)
    data_df[col_name] = None

    start_time = time.time()
    extract_aste(14, 4, data_df, col_name)
    first_lap = time.time() - start_time
    
    num_null = 0
    while data_df[col_name].isna().sum() > 0:
        num_null += data_df[col_name].isna().sum()
        extract_aste(14, 4, data_df, col_name)
    end_time = time.time() - start_time

    print(f"\n한 바퀴: {first_lap}초, 총: {end_time}초, 평균: {end_time / 100}초")
    print(f"총 {num_null}개의 추론 실패 후 재시도")

    print("\n=== Start Evaluation ===\n")

    evaluate_aste(
        data_df, 
        golden_label_col="aste_golden_label", 
        model_prediction_col=col_name,
    )
    