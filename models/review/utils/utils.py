#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[유틸리티 함수 모듈]
- 리뷰 데이터 로드, 전처리, 임베딩 생성, UMAP, 클러스터링, 시각화, API 호출 등
"""

import os
import numpy as np
import pandas as pd
import json
import requests
import time
import umap
import hdbscan
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

def load_data(file_path):
    df = pd.read_csv(file_path)
    print("데이터 로드:", df.shape)
    return df

def load_and_preprocess_reviews(file_path):
    df = pd.read_csv(file_path)
    cols_to_fill = ["category", "name", "url", "meta"]
    df[cols_to_fill] = df.groupby("ID")[cols_to_fill].transform(lambda x: x.ffill())
    meta_df = df[df["review-ID"].astype(str).str.endswith("-0")]
    review_df = df[~df["review-ID"].astype(str).str.endswith("-0")]
    return meta_df, review_df

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

def sentenceBERT_embeddings(embedding_path, df, column="processed", model_name="dragonkue/BGE-m3-ko"):

    print("\n임베딩 파일을 새로 생성합니다...\n")
    model = SentenceTransformer(model_name)
    embeddings = df[column].apply(lambda txt: model.encode(txt, show_progress_bar=False)).tolist()
    emb_matrix = np.array(embeddings)
    np.save(embedding_path, emb_matrix)
    print(f"\n임베딩 파일 저장 완료: {embedding_path}\n")

    print(f"임베딩 Shape:{emb_matrix.shape}\n")
    return emb_matrix

def umap_reduce_embeddings(embedding_matrix, n_components=256, random_state=42):
    num_samples, _ = embedding_matrix.shape
    if n_components >= num_samples:
        print("UMAP 적용 불가: n_components가 데이터 수보다 큽니다. 원본 반환.")
        return embedding_matrix
    reducer = umap.UMAP(n_components=n_components, random_state=random_state)
    reduced = reducer.fit_transform(embedding_matrix)
    print(f"차원 축소 완료: {embedding_matrix.shape} -> {reduced.shape}")
    return reduced

def agglomerative_clustering(emb, distance_threshold=22.0, linkage="ward"):
    clustering = AgglomerativeClustering(distance_threshold=distance_threshold,
                                         n_clusters=None,
                                         compute_full_tree=True,
                                         linkage=linkage)
    labels = clustering.fit_predict(emb)
    print(f"Agglomerative Clustering 완료: 클러스터 수 {np.unique(labels).shape[0]}")
    return labels

def visualize_clustering(emb, cluster_labels, config, category):
    tsne = TSNE(n_components=2, perplexity=30, learning_rate=200, random_state=42)
    emb_2d = tsne.fit_transform(emb)
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(emb_2d[:,0], emb_2d[:,1], c=cluster_labels, cmap="tab10", alpha=0.6)
    plt.colorbar(sc, label="클러스터 번호")
    plt.title("Agglomerative Clustering Algorithm Visualization")
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    # plt.show()
    plt.savefig(os.path.join(config["paths"]["embedding_dir"], f"{category}_cluster_result.png"))  # 결과를 파일로 저장


def evaluate_clustering(emb, cluster_labels, config, category):
    if len(set(cluster_labels)) > 1:
        silhouette = silhouette_score(emb, cluster_labels)
        dbi = davies_bouldin_score(emb, cluster_labels)
        print(f"실루엣 점수: {silhouette:.4f}, Davies-Bouldin Index: {dbi:.4f}")
        
        results = {"category": category, "Silhouette": float(silhouette), "DBI": float(dbi)}

        json_path = os.path.join(config["paths"]["embedding_dir"], f"{category}_clustering_evaluation.json")
        with open(json_path, "w") as f:
            json.dump(results, f, indent=4)
        
        return results
    else:
        print("단일 클러스터로 평가 불가")
        return {"Silhouette": None, "DBI": None}
