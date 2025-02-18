# utils.py
import re
import os
import json
import ast
import pandas as pd

from openai import OpenAI
import argparse


def merge_ocr_data(finetuning_file, ocr_file, output_file):
    """
    finetuning CSV 파일과 OCR CSV 파일을 'img-ID'를 기준으로 병합하여,
    OCR 결과를 finetuning 데이터에 추가한 후 output_file에 저장합니다.
    """
    finetuning_df = pd.read_csv(finetuning_file)
    ocr_df = pd.read_csv(ocr_file)

    # OCR CSV에서 'img-ID'와 'OCR 결과' 컬럼만 사용하고, 컬럼명을 변경
    ocr_df = ocr_df[['img-ID', 'OCR 결과']].rename(columns={'OCR 결과': 'ocr_data'})

    # 'img-ID'를 기준으로 병합 (인덱스로 설정 후 조인)
    updated_df = finetuning_df.set_index('img-ID')
    ocr_df = ocr_df.set_index('img-ID')

    updated_df['ocr_data'] = ocr_df['ocr_data']

    # 인덱스를 컬럼으로 다시 복원하지 않고 저장하려면 index=False 옵션 사용
    updated_df.to_csv(output_file, index=False, encoding='utf-8-sig')


def parse_json_field(json_str):
    """
    'reference' 컬럼의 JSON 문자열을 파싱하여 다음 5개 필드를 추출합니다.
      - 원재료
      - 알레르기(1차)
      - 알레르기(2차)
      - 보관방법(개봉전)
      - 보관방법(개봉후)
    """
    try:
        if isinstance(json_str, str):
            # 작은따옴표를 큰따옴표로 변환하여 올바른 JSON 문자열로 변환
            data = json.loads(json_str.replace("'", "\""))
        else:
            return pd.Series(["오류", "오류", "오류", "오류", "오류"])

        원재료 = ", ".join(data.get("원재료", [])) if isinstance(data.get("원재료"), list) else ""
        알레르기_1차 = ", ".join(data.get("알레르기(1차)", [])) if isinstance(data.get("알레르기(1차)"), list) else ""
        알레르기_2차 = ", ".join(data.get("알레르기(2차)"), []) if isinstance(data.get("알레르기(2차)"), list) else ""

        # 보관방법은 문자열로 변환 후 필요한 값만 추출
        보관방법_raw = str(data.get("보관방법", "{}"))
        try:
            보관방법_dict = ast.literal_eval(보관방법_raw) if "{" in 보관방법_raw else {}
        except (ValueError, SyntaxError):
            보관방법_dict = {}

        보관방법_개봉전 = 보관방법_dict.get("개봉전", "") if isinstance(보관방법_dict, dict) else ""
        보관방법_개봉후 = 보관방법_dict.get("개봉후", "") if isinstance(보관방법_dict, dict) else ""

        return pd.Series([원재료, 알레르기_1차, 알레르기_2차, 보관방법_개봉전, 보관방법_개봉후])
    except (json.JSONDecodeError, TypeError):
        return pd.Series(["오류", "오류", "오류", "오류", "오류"])


def extract_number_from_img_id(img_id):
    """
    'img-ID' 문자열에서 '-' 사이에 있는 숫자를 추출하여 정렬 번호로 반환합니다.
    """
    match = re.search(r'-(\d+)-', str(img_id))
    return int(match.group(1)) if match else float('inf')


def process_ingredient_dataset(input_csv, output_csv):
    """
    학습 데이터셋 혹은 평가 데이터셋 CSV 파일을 후처리하여,
    'reference' 컬럼에 있는 JSON 데이터를 파싱하고 정렬 후 필요한 컬럼만 남겨 output_csv에 저장합니다.
    """
    df = pd.read_csv(input_csv)

    # 'reference' 컬럼의 JSON 데이터를 개별 컬럼으로 분리
    df[["원재료", "알레르기(1차)", "알레르기(2차)", "보관방법(개봉전)", "보관방법(개봉후)"]] = df["reference"].apply(parse_json_field)

    # 'img-ID'에서 번호 추출 후 정렬
    df['정렬번호'] = df['img-ID'].apply(extract_number_from_img_id)
    df.sort_values(by='정렬번호', ascending=True, inplace=True)

    # 필요한 컬럼만 선택
    df = df[["img-ID", "원재료", "알레르기(1차)", "알레르기(2차)", "보관방법(개봉전)", "보관방법(개봉후)"]]

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")


def evaluate_ingredients(finetuning_csv, ocr_csv,
                         system_prompt_file, user_prompt_file,
                         output_csv, model="gpt-4o", api_key=None):
    """
    평가 데이터셋을 처리합니다.
      1. finetuning CSV와 OCR CSV를 'img-ID' 기준으로 병합합니다.
      2. system, user prompt 파일을 불러와서 user prompt의 {ocr_data} 부분을 OCR 데이터로 대체합니다.
      3. OpenAI API를 호출하여 결과를 받아 finetuning 데이터의 'reference' 컬럼에 저장한 후, output_csv에 저장합니다.
    """
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    client = OpenAI()

    # 프롬프트 파일 읽기
    with open(system_prompt_file, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    with open(user_prompt_file, "r", encoding="utf-8") as f:
        user_prompt_template = f.read()

    # CSV 파일 읽기
    finetuning_df = pd.read_csv(finetuning_csv)
    ocr_df = pd.read_csv(ocr_csv)

    # 'img-ID' 기준으로 OCR 데이터를 병합
    merged_df = finetuning_df.merge(ocr_df[['img-ID', 'OCR 결과']], on='img-ID', how='left')

    results = []
    for idx, row in merged_df.iterrows():
        ocr_data = row["OCR 결과"] if pd.notna(row["OCR 결과"]) else "N/A"
        user_prompt = user_prompt_template.replace("{ocr_data}", ocr_data)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            result = completion.choices[0].message.content
        except Exception as e:
            result = f"Error: {str(e)}"

        results.append(result)

    finetuning_df["reference"] = results
    finetuning_df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    
    # 1. 학습 데이터셋 파싱
    print(">> 학습 데이터셋 파싱 중...")
    merge_ocr_data(
        finetuning_file="data/HCX/train/finetuning_273_gpt_human_v2.csv",
        ocr_file="data/OCR/inference/images_273_OCR_row_col.csv",
        output_file="data/HCX/train/HCX_273_gpt_processed_v2.csv"
    )
    print("   → 결과: data/HCX/train/HCX_273_gpt_processed_v2.csv\n")

    # 2. 학습 데이터셋 후처리
    print(">> 학습 데이터셋 후처리 중...")
    process_ingredient_dataset(
        input_csv="data/HCX/train/finetuning_273_gpt_human_v2.csv",
        output_csv="data/HCX/train/images_273_ingredient.csv"
    )
    print("   → 결과: data/HCX/train/images_273_ingredient.csv\n")

    # 3. 평가 데이터셋 생성
    print(">> 평가 데이터셋 생성 중...")
    API_KEY = "YOUR_API_KEY"
    evaluate_ingredients(
        finetuning_csv="data/preprocessed/images_50.csv",
        ocr_csv="data/OCR/inference/images_50_OCR_row_col.csv",
        system_prompt_file="prompt/system_prompt_vf.txt",
        user_prompt_file="prompt/user_prompt_vf.txt",
        output_csv="data/HCX/eval/finetuning_50_gpt.csv",
        model="gpt-4o",
        api_key=API_KEY
    )
    print("   → 결과: data/HCX/eval/finetuning_50_gpt.csv\n")

    # 4. 평가 데이터셋 후처리
    print(">> 평가 데이터셋 후처리 중...")
    process_ingredient_dataset(
        input_csv="data/HCX/eval/finetuning_50_gpt.csv",
        output_csv="data/HCX/eval/images_50_ingredient.csv"
    )
    print("   → 결과: data/HCX/eval/images_50_ingredient.csv\n")

    print("모든 작업이 완료되었습니다.")
