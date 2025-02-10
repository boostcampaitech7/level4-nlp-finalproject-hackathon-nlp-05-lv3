#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[학습 데이터 샘플링 파이프라인]
1. 전처리된 리뷰 데이터에서 골든 및 수동 레이블 데이터를 제외
2. Sentence-BERT 임베딩을 이용하여 리뷰 벡터 생성
3. K-Means 클러스터링으로 900개 클러스터 생성 후 각 클러스터 중심 샘플 선택
4. 대표 샘플 CSV 파일로 저장
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.cluster import KMeans
from tqdm import tqdm
from glob import glob

# utils 모듈에서 임베딩 함수를 import
from utils.utils import sentenceBERT_embeddings

def filter_data(config):
    preprocessed_dir = os.path.join(config["paths"]["preprocessed_dir"])
    csv_files = glob(os.path.join(preprocessed_dir, "*.csv"))
    csv_files = [f for f in glob(os.path.join(preprocessed_dir, "*.csv")) 
                 if not (os.path.basename(f).startswith("meta_") 
                         or os.path.basename(f).endswith("_all.csv"))]
    
    df_list = [pd.read_csv(file) for file in csv_files]
    merged_df = pd.concat(df_list, ignore_index=True)
    merged_output = os.path.join(preprocessed_dir, "processed_reviews_all.csv")
    merged_df.to_csv(merged_output, index=False)
    print(f"[전체 전처리 데이터 저장] {merged_output}\n")

    raw_df = pd.read_csv(merged_output)
    golden_file = os.path.join(config["paths"]["eval_dir"], "aste_annotation_100_golden_label.csv")
    golden_df = pd.read_csv(golden_file)
    df_filtered = raw_df[~raw_df['review-ID'].isin(golden_df['review-ID'])]
    output_filtered = os.path.join(config["paths"]["aste_dir"], "processed_except_GL.csv")
    df_filtered.to_csv(output_filtered, index=False)
    print(f"[골든 라벨 제외 전처리 데이터 저장] {output_filtered}")
    return output_filtered

def perform_kmeans_clustering(embeddings: np.ndarray, num_clusters=900, random_state=42):
    print("K-Means 클러스터링 수행 중...\n")
    kmeans = KMeans(n_clusters=num_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    return kmeans, labels, num_clusters

def select_representative_samples(kmeans, cluster_labels: np.ndarray, num_clusters, embeddings: np.ndarray) -> list:
    selected_idx = []
    for cid in tqdm(range(num_clusters), desc="대표 샘플 선택"):
        indices = np.where(cluster_labels == cid)[0]
        center = kmeans.cluster_centers_[cid]
        closest = indices[np.argmin(np.linalg.norm(embeddings[indices] - center, axis=1))]
        selected_idx.append(closest)
    return selected_idx

def run_train_data_sampling(config):
    print("\n[학습 데이터 샘플링 시작]\n")
    filtered_file = filter_data(config)
    embedding_path = os.path.join(config["paths"]["embedding_dir"], "train_sampling.npy")
    raw_data = pd.read_csv(filtered_file)
    embedding_matrix = sentenceBERT_embeddings(embedding_path, raw_data, column="processed")
    kmeans, labels, num_clusters = perform_kmeans_clustering(embedding_matrix, num_clusters=config["train_data_annotating"]["num_train_data"])
    selected_indices = select_representative_samples(kmeans, labels, num_clusters, embedding_matrix)
    sampled_df = raw_data.iloc[selected_indices].reset_index(drop=True)
    output_file = os.path.join(config["paths"]["aste_dir"], "aste_sampled.csv")
    sampled_df.to_csv(output_file, index=False)
    print("\n[학습 데이터 샘플링 완료]", output_file)

if __name__ == "__main__":
    run_train_data_sampling({
        "paths": {
            "data_dir": "./data",
            "embedding_dir": "./data/embedding_matrics"
        }
    })
