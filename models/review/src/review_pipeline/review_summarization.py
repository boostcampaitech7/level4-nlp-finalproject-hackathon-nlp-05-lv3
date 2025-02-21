#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[리뷰 요약 추출 파이프라인]
- 리뷰 데이터를 기반으로 두 개의 aspect별 요약을 생성:
    1. "맛" (단독)
    2. "배송"과 "포장"을 통합한 "배송 및 포장"
- 각 상품의 원본 리뷰를 활용하여 각 aspect별 긍정/부정 핵심 포인트를 요약하고,
  각 aspect별 고유 리뷰 개수를 산출하여 최종 CSV 파일로 저장한다.
"""

import os
import sys
import time
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from prompt.prompt_loader import load_prompt, load_fewshot
import re

def load_data(file_path):
    df = pd.read_csv(file_path)
    print("데이터 로드:", file_path)
    return df

def expand_inference_data(df, json_column="unsloth_deepseek_32b"):
    expanded = []
    for idx, row in df.iterrows():
        raw_value = row[json_column]

        # 만약 raw_value가 문자열이면 json.loads()를 사용, 이미 리스트면 그대로 사용
        if isinstance(raw_value, str):
            try:
                parsed = json.loads(raw_value)
            except json.JSONDecodeError:
                print(f"JSON 파싱 에러, review-ID: {row.get('review-ID', 'N/A')}")
                continue
        elif isinstance(raw_value, list):
            parsed = raw_value
        else:
            # 그 외 타입인 경우 무시
            continue

        if isinstance(parsed, list):
            for item in parsed:
                new_row = row.copy()
                new_row["aspect"] = item.get("속성", None)
                new_row["opinion"] = item.get("평가", None)
                new_row["sentiment"] = item.get("감정", None)
                expanded.append(new_row)
    expanded_df = pd.DataFrame(expanded)
    expanded_df.reset_index(drop=True, inplace=True)
    expanded_df.ffill(inplace=True)
    return expanded_df

def filter_invalid_value(raw_value):
    """
    unsloth_deepseek_32b 칼럼의 한 값을 전달받아,
    - float(NaN) 또는 "[]" 인 경우 None 반환
    - 정상적인 JSON 문자열이면 파싱해서 반환, 그렇지 않으면 None 반환
    """
    if isinstance(raw_value, float) or (isinstance(raw_value, str) and raw_value.strip() == "[]"):
        return None
    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, list):
            return parsed
        else:
            return None
    except json.JSONDecodeError:
        return None

def load_and_prepare_data(config):
    train_data_path = os.path.join(config["paths"]["inference_dir"], config["inference_data"])
    df_infer = load_data(train_data_path)
    df_infer["unsloth_deepseek_32b"] = df_infer["unsloth_deepseek_32b"].apply(filter_invalid_value)
    df_infer = df_infer.dropna(subset=["unsloth_deepseek_32b"])
    aste_df = expand_inference_data(df_infer, "unsloth_deepseek_32b")
    # 필요 없는 열 제거
    cols_to_drop = ['aste_hcx', 'aste_gpt', 'aste_golden_label']
    aste_df.drop(columns=cols_to_drop, errors='ignore', inplace=True)
    print(f"리뷰 Opinion 데이터 개수: {aste_df.shape[0]}")
    # FILTER_KEYWORDS = "맛|좋"
    # aste_df = aste_df[~aste_df["opinion"].str.contains(FILTER_KEYWORDS)]
    # print(f"필터링 후 리뷰 데이터: {aste_df.shape[0]}")
    return aste_df

def get_prompt_and_fewshot(aspect: str, sentiment: str):
    """
    aspect와 sentiment에 따른 프롬프트와 few-shot 예시를 반환한다.
    프롬프트와 few-shot 예시는 prompt 폴더 내의 파일로 분리되어 관리된다.
    """
    if sentiment == "긍정":
        prompt = load_prompt(prompt_filename="positive_prompt.txt",
                             prompt_dir="./prompt/review_summarization/")
        fewshot = load_fewshot(fewshot_filename="positive_fewshot.json",
                             prompt_dir="./prompt/review_summarization/")
    else:
        prompt = load_prompt(prompt_filename="negative_prompt.txt",
                             prompt_dir="./prompt/review_summarization/")
        fewshot = load_fewshot(fewshot_filename="negative_fewshot.json",
                             prompt_dir="./prompt/review_summarization/")
    return prompt, fewshot

def inference(query: str, sentiment: str, aspect: str) -> str:
    load_dotenv(os.path.expanduser("~/.env"))
    AUTHORIZATION = os.getenv("AUTHORIZATION")
    X_NCP_CLOVASTUDIO_REQUEST_ID = os.getenv("X_NCP_CLOVASTUDIO_REQUEST_ID")
    if not AUTHORIZATION or not X_NCP_CLOVASTUDIO_REQUEST_ID:
        raise ValueError("필수 API 인증 정보가 .env에 설정되어 있지 않습니다.")
    headers = {
        'Authorization': AUTHORIZATION,
        'X-NCP-CLOVASTUDIO-REQUEST-ID': X_NCP_CLOVASTUDIO_REQUEST_ID,
        'Content-Type': 'application/json; charset=utf-8',
    }
    prompt, fewshot = get_prompt_and_fewshot(aspect, sentiment)
    # query가 문자열인데 리스트 형태의 표현이면 join
    if query.startswith("[") and query.endswith("]"):
        try:
            import ast
            q_list = ast.literal_eval(query)
            if isinstance(q_list, list):
                query = " ".join(q_list)
        except Exception as e:
            print("Query parsing error:", e)
            
    messages = [{"role": "system", "content": prompt}]
    for example in fewshot:
        # 만약 fewshot의 query가 리스트면 join
        query_text = " ".join(example["query"]) if isinstance(example["query"], list) else example["query"]
        messages.append({"role": "user", "content": query_text})
        messages.append({"role": "assistant", "content": example["answer"]})
    messages.append({"role": "user", "content": query})
    
    request_data = {
        'messages': messages,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 1024,
        'temperature': 0.5,
        'repeatPenalty': 5.0,
        'stopBefore': [],
        'includeAiFilters': False,
        'seed': 42
    }
    try:
        response = requests.post(
            "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
            headers=headers, json=request_data
        )
        response.raise_for_status()
        response_json = response.json()
        if response_json.get("status", {}).get("code") == "20000":
            output_text = response_json["result"]["message"]["content"]
            return output_text
        else:
            return f"API Error: {response_json.get('status', {}).get('message')}"
    except requests.exceptions.RequestException as e:
        return f"Request Error: {e}"

def robust_inference(query: str, sentiment: str, aspect: str, retry_delay: int = 2) -> str:
    while True:
        result = inference(query, sentiment, aspect)
        if not (result.startswith("API Error") or result.startswith("Request Error")):
            print(result)
            return result
        print("API 오류 발생, 다시 시도합니다...")
        time.sleep(retry_delay)

def summarize_opinions_with_original(reviews: list, sentiment: str, aspect: str) -> tuple:
    unique_reviews = list(set(reviews))
    sample_reviews = unique_reviews[:20]
    if not sample_reviews:
        return "없습니다.", "없습니다."
    reviews_str = str(sample_reviews)
    summary = robust_inference(reviews_str, sentiment, aspect)
    summary = summary.strip()[1:-1] if summary.startswith('"') and summary.endswith('"') else summary
    return summary, reviews_str

def process_product(product_id: str, aste_df: pd.DataFrame) -> dict:
    SENTIMENT_POSITIVE = "긍정"
    SENTIMENT_NEGATIVE = "부정"
    product_reviews = aste_df[aste_df["review-ID"].str.contains(product_id)]
    product_name = product_reviews["name"].dropna().unique()[0]
    product_dict = {
        "ID": product_id,
        "상품명": product_name,
    }
    # 맛 단독 처리
    pos_reviews_m = product_reviews[(product_reviews["aspect"] == "맛") & (product_reviews["sentiment"] == SENTIMENT_POSITIVE)]["review"].tolist()
    neg_reviews_m = product_reviews[(product_reviews["aspect"] == "맛") & (product_reviews["sentiment"] != SENTIMENT_POSITIVE)]["review"].tolist()
    summary_pos_m, _ = summarize_opinions_with_original(pos_reviews_m, SENTIMENT_POSITIVE, "맛")
    summary_neg_m, _ = summarize_opinions_with_original(neg_reviews_m, SENTIMENT_NEGATIVE, "맛")
    product_dict["맛-긍정"] = summary_pos_m
    product_dict["맛-부정"] = summary_neg_m

    # 배송 및 포장 통합 처리: 배송과 포장 둘 다 포함
    pos_reviews_dp = product_reviews[((product_reviews["aspect"] == "배송") | (product_reviews["aspect"] == "포장")) &
                                      (product_reviews["sentiment"] == SENTIMENT_POSITIVE)]["review"].tolist()
    neg_reviews_dp = product_reviews[((product_reviews["aspect"] == "배송") | (product_reviews["aspect"] == "포장")) &
                                      (product_reviews["sentiment"] != SENTIMENT_POSITIVE)]["review"].tolist()
    summary_pos_dp, _ = summarize_opinions_with_original(pos_reviews_dp, SENTIMENT_POSITIVE, "배송 및 포장")
    summary_neg_dp, _ = summarize_opinions_with_original(neg_reviews_dp, SENTIMENT_NEGATIVE, "배송 및 포장")
    product_dict["배송 및 포장-긍정"] = summary_pos_dp
    product_dict["배송 및 포장-부정"] = summary_neg_dp

    return product_dict

def update_summary_counts(summary_df: pd.DataFrame, aste_df: pd.DataFrame) -> pd.DataFrame:
    summary_df["num 맛-긍정"] = None
    summary_df["num 맛-부정"] = None
    summary_df["num 배송 및 포장-긍정"] = None
    summary_df["num 배송 및 포장-부정"] = None

    for idx, row in summary_df.iterrows():
        product_id = row["ID"]
        product_reviews = aste_df[aste_df["review-ID"].str.contains(product_id)]
        num_m_pos = len(product_reviews[(product_reviews["aspect"] == "맛") & (product_reviews["sentiment"] == "긍정")]["review"].unique())
        num_m_neg = len(product_reviews[(product_reviews["aspect"] == "맛") & (product_reviews["sentiment"] != "긍정")]["review"].unique())
        num_dp_pos = len(product_reviews[((product_reviews["aspect"] == "배송") | (product_reviews["aspect"] == "포장")) & (product_reviews["sentiment"] == "긍정")]["review"].unique())
        num_dp_neg = len(product_reviews[((product_reviews["aspect"] == "배송") | (product_reviews["aspect"] == "포장")) & (product_reviews["sentiment"] != "긍정")]["review"].unique())

        summary_df.at[idx, "num 맛-긍정"] = num_m_pos
        summary_df.at[idx, "num 맛-부정"] = num_m_neg
        summary_df.at[idx, "num 배송 및 포장-긍정"] = num_dp_pos
        summary_df.at[idx, "num 배송 및 포장-부정"] = num_dp_neg

    return summary_df

def extract_product_id(review_id):
    match = re.match(r"(emart-\d+)-\d+", review_id)
    return match.group(1) if match else review_id  # 매칭 실패 시 원래 값 반환

def load_and_prepare_data(config):
    train_data_path = os.path.join(config["paths"]["inference_dir"], config["inference_data"])
    df_infer = load_data(train_data_path)
    df_infer["unsloth_deepseek_32b"] = df_infer["unsloth_deepseek_32b"].apply(filter_invalid_value)
    df_infer = df_infer.dropna(subset=["unsloth_deepseek_32b"])
    aste_df = expand_inference_data(df_infer, "unsloth_deepseek_32b")
    cols_to_drop = ['aste_hcx', 'aste_gpt', 'aste_golden_label']
    aste_df.drop(columns=cols_to_drop, errors='ignore', inplace=True)
    print(f"리뷰 Opinion 데이터 개수: {aste_df.shape[0]}")
    print(f"필터링 후 리뷰 데이터: {aste_df.shape[0]}")
    return aste_df


def run_review_summarization(config):
    print("\n[리뷰 요약 추출 시작]\n")
    aste_df = load_and_prepare_data(config)
    product_ids = list({extract_product_id(item) for item in aste_df["review-ID"].tolist()})
    print(f"처리할 상품 수: {len(product_ids)}")
    summary_list = []
    for prod_id in product_ids:
        prod_summary = process_product(prod_id, aste_df)
        summary_list.append(prod_summary)
    summary_df = pd.DataFrame(summary_list)
    summary_df = update_summary_counts(summary_df, aste_df)
    final_columns = ["ID", "상품명", "맛-긍정", "맛-부정", "배송 및 포장-긍정", "배송 및 포장-부정", 
                     "num 맛-긍정", "num 맛-부정", "num 배송 및 포장-긍정", "num 배송 및 포장-부정"]
    summary_df = summary_df[final_columns]
    output_file = os.path.join(config["paths"]["final_outputs_dir"], "summarization.csv")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    summary_df.to_csv(output_file, index=False)
    print(f"최종 요약 결과가 저장되었습니다: {output_file}")
    print("\n[리뷰 요약 추출 완료]\n")
    return summary_df


if __name__ == "__main__":
    run_review_summarization({
        "paths": {
            "inference_dir": "./data/aste/inference",
            "preprocessed_dir": "./data/preprocessed",
            "final_outputs_dir": "../final_outputs"
        },
        "inference_data": "inferenced_reviews_snacks_meals_2.csv"
    })
