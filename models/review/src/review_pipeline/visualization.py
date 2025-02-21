#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[클러스터링 결과 시각화 및 정량적 평가 파이프라인]
- 입력 CSV 파일 로부터 추천 키워드 별로 상품을 재정렬하여 최종 추천 CSV 파일을 생성한다.
- 최종 출력 CSV 파일은 다음 열로 구성된다:
    카테고리, 키워드, ID, 상품명, opinion 개수
- 본 파이프라인은 config를 활용하고, prompt 폴더의 프롬프트 및 few-shot 예시를 참고하여 API 호출을 수행한다.
- run_keyword_recommendation() 함수를 통해 전체 파이프라인을 실행한다.
"""

import os, sys
import re
import json
import time
import requests
import pandas as pd
import numpy as np
import yaml

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from utils.utils import load_data, expand_inference_data, sentenceBERT_embeddings, umap_reduce_embeddings, agglomerative_clustering, visualize_clustering, evaluate_clustering

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


#########################################################
# 최종 평가 실행 함수
#########################################################

print("\n[추천 키워드 기반 상품 재정렬 시각화, 정량적 평가]\n")

# config 파일을 config/config.yaml에서 로드 (파일 위치: 프로젝트 루트/config/config.yaml)
config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "config", "config.yaml"
)

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


# 1. 데이터 로드 및 전처리
aste_df = load_and_prepare_data(config)

# 2. 긍정 의견만 선택 (추천 키워드는 긍정 리뷰 기반)
infer_pos = aste_df[aste_df["sentiment"] == "긍정"]
infer_pos.loc[:, 'category'] = infer_pos['category'].replace({'아이간식': '라면/간편식'})

category_map = {
    "과자/빙과": "snacks",
    "라면/간편식": "meals"
}

infer_pos["category"] = infer_pos["category"].map(category_map).fillna(infer_pos["category"])

# 카테고리별로 DataFrame 분할
category_dfs = {category: df for category, df in infer_pos.groupby("category")}

for category, df_cat in category_dfs.items():
    # 3. 리뷰 텍스트 임베딩 생성 (opinion 열 사용)
    embedding_file = os.path.join(config["paths"]["embedding_dir"], f"deepseek_inference_{category}.npy")
    embedding_matrix = sentenceBERT_embeddings(embedding_file, df=df_cat, column="opinion")

    # 4. UMAP 차원 축소
    reduced_embeddings = umap_reduce_embeddings(embedding_matrix, n_components=256)

    # 5. 클러스터링 (Agglomerative Clustering 사용, 임계값 조정)
    cluster_labels = agglomerative_clustering(reduced_embeddings, distance_threshold=21.5)
    df_cat['cluster_label'] = cluster_labels

    # 6. 클러스터 시각화
    visualize_clustering(reduced_embeddings, cluster_labels, config, category)

    # 7. 평가 Metric
    evaluate_clustering(reduced_embeddings, cluster_labels, config, category)
