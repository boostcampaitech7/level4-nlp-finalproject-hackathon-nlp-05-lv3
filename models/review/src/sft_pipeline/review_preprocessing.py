#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[리뷰 전처리 파이프라인]
- 원본 리뷰 CSV 파일에서 텍스트를 전처리 (특수문자 제거, 개행 교체, 영어/숫자 필터, 공백 정규화, 반복 제거, 짧은 텍스트 배제)
- T5 맞춤법 교정 모델로 오타 교정 수행
"""

import re
import os, sys
import torch
import pandas as pd
from glob import glob
from tqdm import tqdm
from konlpy.tag import Hannanum
from transformers import T5ForConditionalGeneration, T5Tokenizer
from utils.utils import load_and_preprocess_reviews

hannanum = Hannanum()

def remove_special_chars(text):
    return re.sub(r'[^a-zA-Z0-9가-힣\s]', '', text) if isinstance(text, str) else ""

def replace_newlines(text):
    return re.sub(r'[\r\n]+', ' ', text).strip() if isinstance(text, str) else ""

def filter_text_by_english_ratio(text, ratio=0.3):
    if not isinstance(text, str) or not text.strip():
        return ""
    total = len(text)
    eng_count = len(re.findall(r"[a-zA-Z]", text))
    return text if (eng_count / total if total > 0 else 0) <= ratio else ""

def filter_text_by_number_ratio(text, ratio=0.3):
    if not isinstance(text, str) or not text.strip():
        return ""
    total = len(text)
    num_count = len(re.findall(r"[0-9]", text))
    return text if (num_count / total if total > 0 else 0) <= ratio else ""

def normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip() if isinstance(text, str) else ""

def remove_repetition(text):
    def is_valid_word(word):
        pos_tags = hannanum.pos(word)
        for token, pos in pos_tags:
            if token == word:
                return True
        return False
    def compress_token(token):
        if is_valid_word(token):
            return token
        n = len(token)
        for L in range(1, n // 2 + 1):
            segment = token[:L]
            if segment * (n // L) == token:
                return segment
        return token
    def compress_token_list(tokens):
        n = len(tokens)
        for k in range(1, n // 2 + 1):
            block = tokens[:k]
            if block * (n // k) == tokens:
                return block
        return tokens
    if not text or not isinstance(text, str):
        return ""
    tokens = text.split()
    tokens = [compress_token(token) for token in tokens]
    tokens = compress_token_list(tokens)
    return " ".join(tokens).strip()

def remove_short_text(text, n=5):
    return text if len(text) > n else ''

MODEL_NAME = "j5ng/et5-typos-corrector"
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = model.to(device)

def batch_correct_typos(df, target_col, batch_size=100):
    if target_col not in df.columns:
        raise ValueError("대상 컬럼이 데이터프레임에 없습니다.")
    df = df.copy()
    df["processed"] = None
    for i in tqdm(range(0, len(df), batch_size), desc="배치 처리"):
        batch_texts = df[target_col].iloc[i : i + batch_size].tolist()
        input_texts = ["맞춤법을 고쳐주세요: " + text for text in batch_texts]
        encodings = tokenizer(input_texts, return_tensors="pt", padding=True, truncation=True, max_length=128)
        input_ids = encodings.input_ids.to(device)
        attention_mask = encodings.attention_mask.to(device)
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=128,
            num_beams=5,
            early_stopping=True
        )
        output_texts = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        num_rows = min(len(df) - i, len(output_texts))
        col_idx = df.columns.get_loc("processed")
        df.iloc[i : i + num_rows, col_idx] = output_texts[:num_rows]
    return df

def run_review_preprocessing(config):
    print("\n[리뷰 전처리 시작]\n")
    input_dir = os.path.join(config["paths"]["crawled_reviews_dir"])
    output_dir = os.path.join(config["paths"]["preprocessed_dir"])
    os.makedirs(output_dir, exist_ok=True)
    csv_files = glob(os.path.join(input_dir, "*.csv"))
    if not csv_files:
        print("처리할 CSV 파일이 없습니다.")
        return
    for src_file in csv_files:
        base_name = os.path.basename(src_file).replace("crawled_", "processed_", 1)
        dest_file = os.path.join(output_dir, base_name)
        meta_base_name = os.path.basename(src_file).replace("crawled_", "meta_", 1)
        meta_dest_file = os.path.join(output_dir, meta_base_name)
        try:
            meta_df, df = load_and_preprocess_reviews(src_file)
            meta_df.to_csv(meta_dest_file, index=False)
        except Exception as e:
            print(f"파일 로드 실패 ({src_file}): {e}")
            continue
        tqdm.pandas()
        df["step_special"] = df["review"].progress_apply(remove_special_chars)
        df["step_newline"] = df["step_special"].apply(replace_newlines)
        df["step_eng_filter"] = df["step_newline"].apply(filter_text_by_english_ratio)
        df["step_num_filter"] = df["step_eng_filter"].apply(filter_text_by_number_ratio)
        df["step_whitespace"] = df["step_num_filter"].apply(normalize_whitespace)
        df["step_repetition"] = df["step_whitespace"].progress_apply(remove_repetition)
        df["step_length"] = df["step_repetition"].apply(remove_short_text)
        df = df[(df["step_length"] != "") & df["step_length"].notna()]
        df = batch_correct_typos(df, "step_length", batch_size=100)
        drop_cols = ["step_special", "step_newline", "step_eng_filter",
                     "step_num_filter", "step_whitespace", "step_repetition", "step_length"]
        df.drop(columns=drop_cols, inplace=True)
        df.to_csv(dest_file, index=False)
        print(f"\n[전처리 데이터 저장] {dest_file}\n")
    print("\n[리뷰 전처리 완료]\n")

if __name__ == "__main__":
    run_review_preprocessing({
        "paths": {
            "data_dir": "./data",
            "crawled_reviews": "./data/crawled_reviews",
            "preprocessed_dir": "./data/preprocessed"
        }
    })
