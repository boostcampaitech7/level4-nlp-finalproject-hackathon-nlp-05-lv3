import argparse
import pandas as pd
import time
import re
import json
from tqdm import tqdm

from unsloth import FastLanguageModel
from utils.evaluate import evaluate_aste  # 평가 함수 임포트 (경로에 맞게 수정)


def load_model():
    """모델과 토크나이저를 로드합니다."""
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name='./output_zeroshot/checkpoint-336',
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

### 예시:
예시를 참고하여 논리적으로 사고하되, 불필요한 과정을 생략하고 간결하게 답변하세요.

예시 1.
이번에 많이 주문했는데 잘 도착했고요 계란도 깨진 거 없이 잘 받았어요 유통 기한도 넉넉하고 만족합니다.
[{{'속성': '배송', '평가': '잘 도착했다.', '감정': '긍정'}}, {{'속성': '배송', '평가': '안전하다.', '감정': '긍정'}}, {{'속성': '상품', '평가': '유통기한이 넉넉하다.', '감정': '긍정'}}, {{'속성': '상품', '평가': '만족스럽다.', '감정': '긍정'}}]

예시 2.
배송 빠르고 좋습니다.
[{{'속성': '배송', '평가': '빠르다.', '감정': '긍정'}}, {{'속성': '배송', '평가': '좋다.', '감정': '긍정'}}]

예시 3.
원래 잘 먹던 거라 재구매입니다.
[{{'속성': '상품', '평가': '자주 먹는다.', '감정': '긍정'}}, {{'속성': '상품', '평가': '재구매다.', '감정': '긍정'}}]

예시 4.
비교해 보려고 사 봤어요. 신선하고 맛있네요.
[{{"속성": "상품", "평가": "비교해보려 구매했다.", "감정": "중립"}}, {{'속성': '신선도', '평가': '신선하다.', '감정': '긍정'}}, {{'속성': '맛', '평가': '맛있다.', '감정': '긍정'}}]

예시 5.
리뷰 보고 주문했는데 기대되네요.
[]

예시 6.
노브랜드 저렴하고 좋아요.
[{{'속성': '가격', '평가': '저렴하다.', '감정': '긍정'}}, {{'속성': '상품', '평가': '좋다.', '감정': '긍정'}}]

예시 7.
치즈피자를 좋아해서 맛있게 잘 먹었어요 비교적 도톰해서 금방 배 불러져요 맛있고 배부르게 잘 먹었어요.
[{{'속성': '맛', '평가': '맛있다.', '감정': '긍정'}}, {{'속성': '양', '평가': '도톰해서 금방 배부르다.', '감정': '긍정'}}, {{'속성': '상품', '평가': '잘 먹었다.', '감정': '긍정'}}]

예시 8.
우유랑 먹어도 맛있고 그냥 과자처럼 먹어도 맛있어요.
[{{'속성': '맛', '평가': '우유랑 먹으면 맛있다.', '감정': '긍정'}}, {{'속성': '맛', '평가': '그냥 먹어도 맛있다.', '감정': '긍정'}}]

예시 9.
새우깡이 당길 때가 있어요 강추드립니다 재구매하려고요 저렴하게 잘 샀어요.
[{{'속성': '맛', '평가': '당기는 맛이다.', '감정': '긍정'}}, {{'속성': '상품', '평가': '추천한다.', '감정': '긍정'}}, {{'속성': '상품', '평가': '재구매 의사 있다.', '감정': '긍정'}}, {{'속성': '가격', '평가': '저렴하다.', '감정': '긍정'}}]

예시 10.
떨어지면 다시 채워 넣고 먹고 있어요 너무 맛있어요.
[{{'속성': '상품', '평가': '항상 재구매한다.', '감정': '긍정'}}, {{'속성': '맛', '평가': '맛있다.', '감정': '긍정'}}]

### 입력:
{review}
<think>
"""


def inference(review_text: str, model, tokenizer):
    """
    입력 리뷰에 대해 모델을 통한 추론을 수행합니다.
    반환: chain-of-thought(cot)와 실제 답변(ans)
    """
    messages = [{"role": "user", "content": PROMPT_TEMPLATE.format(review=review_text)}]
    print("입력 메시지:", messages)

    # 채팅 템플릿 적용 (문자열 생성)
    formatted_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    model_inputs = tokenizer([formatted_text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    # 입력 토큰 길이 이후의 토큰만 추출
    generated_ids = [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # chain-of-thought와 최종 답변 분리 (<think> 태그 기준)
    cot = response.split("</think>")[0].strip()
    ans = response.split("</think>")[-1].strip()
    
    return cot, ans

def post_process_answer(answer: str):
    """
    모델의 답변에서 JSON 코드 블록을 추출하고 파싱합니다.
    """
    match = re.search(r"```json\s*(.*?)\s*```", answer, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = answer  # 코드 블록이 없으면 전체 텍스트 사용

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print("JSON 파싱 에러:", e)
        data = None
    return data

def run_inference_on_dataframe(df: pd.DataFrame, model, tokenizer, num_samples: int = None) -> pd.DataFrame:
    """
    DataFrame의 각 리뷰에 대해 모델 추론을 수행하고, 결과 및 소요 시간을 기록합니다.
    JSON 파싱에 실패한 경우 최대 20회까지 재시도하며, 각 리뷰별 실패 횟수를 failure_counts 리스트에 저장합니다.
    """
    times = []
    failure_counts = []  # 각 리뷰별 재시도(실패) 횟수를 저장할 리스트
    if num_samples is not None:
        df = df.head(num_samples)
    
    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Inference"):
        review_text = row["processed"]
        start_time = time.time()
        attempts = 0  # 재시도 횟수 (성공 시 0이면 최초 시도에 성공한 것)
        ans_json = None
        
        # 최대 20회 시도 (최초 시도 포함하여 최대 20번)
        while attempts < 20:
            cot, ans = inference(review_text, model, tokenizer)
            ans_json = post_process_answer(ans)
            print(ans_json)
            if ans_json is not None:
                break
            attempts += 1
            print(f"JSON 추출 실패, 재시도 {attempts}회")
        
        if ans_json is None:
            print("최대 재시도 횟수(20회)를 초과했습니다. 결과를 None으로 저장합니다.")
        elapsed = time.time() - start_time
        times.append(elapsed)
        failure_counts.append(attempts)
        print(f"처리 시간: {elapsed:.2f}초, 실패 횟수: {attempts}")
        print("\n" + "=" * 60 + "\n")
        
        # 결과를 새로운 컬럼에 저장 (JSON 문자열로)
        df.loc[idx, "unsloth_deepseek_32b"] = json.dumps(ans_json, ensure_ascii=False)
    
    print("전체 처리 시간 리스트:", times)
    if times:
        print("평균 처리 시간: {:.2f}초".format(sum(times) / len(times)))
    print("각 리뷰별 재시도 실패 횟수:", failure_counts)
    return df

def main():
    parser = argparse.ArgumentParser(description="aste 모델 추론 및 평가 스크립트")
    parser.add_argument("--input_csv", type=str, required=True,
                        help="입력 CSV 파일 경로 (예: aste_annotation_100_gpt_after.csv)")
    parser.add_argument("--output_csv", type=str, default=None,
                        help="출력 CSV 파일 경로 (저장할 경우)")
    parser.add_argument("--num_samples", type=int, default=None,
                        help="추론할 샘플 개수 (ID 필터링 후 지정 가능)")
    parser.add_argument("--selected_review_ids", type=str, nargs="*", default=None,
                        help="평가할 특정 review-ID 목록 (예: emart-118 emart-50 ...)")
    args = parser.parse_args()

    model, tokenizer = load_model()

    df = pd.read_csv(args.input_csv)
    print(f"총 {len(df)}개의 리뷰 로드됨.")

    # 만약 특정 ID들이 지정되었다면 필터링
    if args.selected_review_ids:
        df = df[df["review-ID"].isin(args.selected_review_ids)]
        print(f"선택된 리뷰: {df['review-ID'].tolist()}")
        print(f"총 {len(df)}개의 리뷰가 선택됨.")
    
    # 만약 num_samples 옵션이 있다면 head()를 사용 (선택된 ID의 개수보다 작으면 전체가 사용됨)
    if args.num_samples is not None:
        df = df.head(args.num_samples)
    
    print("최종 데이터 수:", len(df))

    df = run_inference_on_dataframe(df, model, tokenizer, num_samples=args.num_samples)

    evaluate_aste(
        df.head(args.num_samples),
        golden_label_col="aste_golden_label",
        model_prediction_col="unsloth_deepseek_32b"
    )

    if args.output_csv:
        df.to_csv(args.output_csv, index=False)
        print(f"결과가 {args.output_csv}에 저장되었습니다.")

if __name__ == "__main__":
    main()