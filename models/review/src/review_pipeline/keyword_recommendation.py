#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[추천 키워드 기반 상품 재정렬 파이프라인]
- 입력 CSV 파일 로부터 추천 키워드 별로 상품을 재정렬하여 최종 추천 CSV 파일을 생성한다.
- 최종 출력 CSV 파일은 다음 열로 구성된다:
    카테고리, 키워드, ID, 상품명, opinion 개수
"""

import os
import re
import json
import time
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from utils.utils import load_data, expand_inference_data, sentenceBERT_embeddings, umap_reduce_embeddings, agglomerative_clustering, visualize_clustering, evaluate_clustering
from prompt.prompt_loader import load_prompt, load_fewshot

#########################################################
# 데이터 전처리 및 확장 관련 함수
#########################################################

def filter_invalid_value(raw_value):
    """
    unsloth_deepseek_32b 칼럼의 값을 전달받아,
      - float(NaN) 또는 "[]"인 경우 None 반환
      - 정상적인 JSON 문자열이면 파싱 후 리스트 반환, 그렇지 않으면 None 반환
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
    """
    config에 명시된 경로와 파일명을 활용하여 입력 CSV 파일을 로드하고,
    unsloth_deepseek_32b 칼럼의 값을 파싱한 후 확장한다.
    불필요한 열은 삭제한다.
    """
    train_data_path = os.path.join(config["paths"]["inference_dir"], config["inference_data"])
    df_infer = load_data(train_data_path)
    df_infer["unsloth_deepseek_32b"] = df_infer["unsloth_deepseek_32b"].apply(filter_invalid_value)
    df_infer = df_infer.dropna(subset=["unsloth_deepseek_32b"])
    aste_df = expand_inference_data(df_infer, "unsloth_deepseek_32b")
    cols_to_drop = ['aste_hcx', 'aste_gpt', 'aste_golden_label']
    aste_df.drop(columns=cols_to_drop, errors='ignore', inplace=True)
    print(f"리뷰 Opinion 데이터 개수: {aste_df.shape[0]}")
    return aste_df

def extract_product_id(review_id):
    """
    review-ID 형식이 "emart-(숫자)-(숫자)"인 경우,
    첫 번째 부분("emart-숫자")를 추출하여 상품 ID로 사용한다.
    """
    match = re.match(r"(emart-\d+)-\d+", review_id)
    return match.group(1) if match else review_id

#########################################################
# 클러스터링 및 추천 키워드 생성 관련 함수
#########################################################

def get_sorted_clusters(df, cluster_column="cluster_label"):
    """
    클러스터 라벨별 크기를 계산하여 정렬된 DataFrame 반환
    """
    cluster_sizes = df[cluster_column].value_counts().reset_index()
    cluster_sizes.columns = [cluster_column, "size"]
    return cluster_sizes[cluster_sizes[cluster_column] != -1].sort_values(by="size", ascending=False)

def hcx_generate_cluster_keywords(df, sorted_clusters, text_column="review", cluster_column="cluster_label"):
    """
    각 클러스터에 대해 HCX API를 활용하여 대표 키워드를 생성한다.
    """
    id_keyword_map = {}
    for cluster in sorted_clusters[cluster_column]:
        size = sorted_clusters[sorted_clusters[cluster_column] == cluster]['size'].values[0]
        print(f"Cluster {cluster} (Size: {size})")
        cluster_texts = df[df[cluster_column] == cluster][text_column]
        unique_texts = list(set(cluster_texts.to_list()))[:50]
        print("샘플 리뷰:", unique_texts)
        keyword = robust_inference(str(unique_texts))
        id_keyword_map[cluster] = keyword.strip().strip('"')
        print("생성된 키워드:", id_keyword_map[cluster])
        print("-" * 80)
    return id_keyword_map

def generate_recommendations(df, id_keyword_map, selected_clusters):
    """
    선택된 클러스터별로, 각 클러스터 내에서 최소 2회 이상 등장한 상품을 대상으로
    추천 상품 DataFrame을 생성한다.
    최종 출력 열은:
      카테고리, 키워드, ID, 상품명, opinion 개수
    """
    result = pd.DataFrame(columns=["카테고리", "키워드", "ID", "상품명", "opinion 개수"])
    for cluster in selected_clusters:
        # 상품명별 빈도수 계산 (5회 이상 등장한 경우만)
        targets = df[df["cluster_label"] == cluster].value_counts(subset=["name"])
        targets = targets[targets >= 5]
        items = [item[0] for item in targets.keys().tolist()]
        # 각 상품의 review-ID에서 상품 ID 추출
        ids = [extract_product_id(df[df["name"] == name]["review-ID"].values[0]) for name in items]
        # 카테고리는 각 상품의 "category" 열의 첫 번째 값 사용
        categories = [df[df["name"] == name]["category"].values[0] for name in items]
        keyword = id_keyword_map.get(cluster, "")
        for item, count, pid, cat in zip(items, targets.tolist(), ids, categories):
            temp_df = pd.DataFrame({
                "카테고리": [cat],
                "키워드": [keyword],
                "ID": [pid],
                "상품명": [item],
                "opinion 개수": [count]
            })
            result = pd.concat([result, temp_df], ignore_index=True)
    return result

def get_prompt_and_fewshot():
    """
    aspect와 sentiment에 따른 프롬프트와 few-shot 예시를 반환한다.
    프롬프트와 few-shot 예시는 prompt 폴더 내의 파일로 분리되어 관리된다.
    """
    prompt = load_prompt(prompt_filename="recommendation_prompt.txt",
                            prompt_dir="./prompt/keyword_recommendation/")
    fewshot = load_fewshot(fewshot_filename="recommendation_fewshot.json",
                            prompt_dir="./prompt/keyword_recommendation/")
    return prompt, fewshot

def robust_inference(query, retry_delay=2):
    """
    API 요청이 실패하면 재시도하는 함수 (추천 키워드 생성을 위해 HCX API 호출)
    """
    while True:
        result = inference(query)
        if not (result.startswith("API Error") or result.startswith("Request Error")):
            return result
        print("API 오류 발생, 다시 시도합니다...")
        time.sleep(retry_delay)

def inference(query):
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
    prompt, fewshot = get_prompt_and_fewshot()

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
        response = requests.post("https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003", headers=headers, json=request_data)
        response.raise_for_status()
        response_json = response.json()
        if response_json.get("status", {}).get("code") == "20000":
            output_text = response_json["result"]["message"]["content"]
            return output_text
        else:
            return f"API Error: {response_json.get('status', {}).get('message')}"
    except requests.exceptions.RequestException as e:
        return f"Request Error: {e}"

#########################################################
# 최종 추천 파이프라인 실행 함수
#########################################################

def run_keyword_recommendation(config):
    print("\n[추천 키워드 기반 상품 재정렬 파이프라인 시작]\n")
    
    # 데이터 로드 및 전처리
    aste_df = load_and_prepare_data(config)
    
    # 긍정 의견만 선택 (추천 키워드는 긍정 리뷰 기반)
    infer_pos = aste_df[aste_df["sentiment"] == "긍정"]
    infer_pos.loc[:, 'category'] = infer_pos['category'].replace({'아이간식': '라면/간편식'})

    category_map = {
        "과자/빙과": "snacks",
        "라면/간편식": "meals"
    }

    infer_pos["category"] = infer_pos["category"].map(category_map).fillna(infer_pos["category"])

    # 카테고리별로 DataFrame 분할
    category_dfs = {category: df for category, df in infer_pos.groupby("category")}

    all_recommendations = []  # 전체 카테고리의 추천 결과를 저장할 리스트
    
    # 각 카테고리별로 전체 파이프라인 실행
    for category, df_cat in category_dfs.items():
        print(f"\n[카테고리: {category} 처리 시작]\n")
        
        # 1) 임베딩 매트릭스 생성
        embedding_file = os.path.join(config["paths"]["embedding_dir"], f"deepseek_inference_{category}.npy")
        embedding_matrix = sentenceBERT_embeddings(embedding_file, df=df_cat, column="opinion")
        
        # 2) UMAP 차원 축소
        reduced_embeddings = umap_reduce_embeddings(embedding_matrix, n_components=256)
        
        # 3) 클러스터링 (Agglomerative Clustering 사용, 임계값 조정)
        cluster_labels = agglomerative_clustering(reduced_embeddings, distance_threshold=21.5)
        df_cat['cluster_label'] = cluster_labels
                
        # 4) 클러스터별 정렬 및 키워드 생성
        sorted_clusters = get_sorted_clusters(df_cat, cluster_column="cluster_label")
        id_keyword_map = hcx_generate_cluster_keywords(df_cat, sorted_clusters, text_column="review", cluster_column="cluster_label")
        
        # 5) 추천 대상 클러스터 선택 (모든 클러스터 사용)
        selected_clusters = sorted_clusters["cluster_label"].tolist()
        
        # 6) 추천 상품 생성
        recommendation_df = generate_recommendations(df_cat, id_keyword_map, selected_clusters)
        final_columns = ["카테고리", "키워드", "ID", "상품명", "opinion 개수"]
        recommendation_df = recommendation_df[final_columns]
        
        # 7) 각 카테고리별 CSV 파일 저장
        output_file = os.path.join(config["paths"]["final_outputs_dir"], f"recommendation_{category}.csv")
        recommendation_df.to_csv(output_file, index=False)
        print(f"카테고리 {category}의 추천 결과가 저장되었습니다: {output_file}")
        
        all_recommendations.append(recommendation_df)
        print(f"\n[카테고리: {category} 처리 완료]\n")
        
    return all_recommendations

if __name__ == "__main__":
    # config를 활용하여 경로 및 파일명을 모듈화
    config = {
        "paths": {
            "inference_dir": "./data/aste/inference",
            "embedding_dir": "./data/embedding_matrics",
            "final_outputs_dir": "../final_outputs"
        },
        "inference_data": "inferenced_reviews_snacks_meals_temp.csv"
    }
    run_keyword_recommendation(config)
