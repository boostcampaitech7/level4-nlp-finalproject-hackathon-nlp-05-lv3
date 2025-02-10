#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[학습데이터 생성 파이프라인]
- 샘플 데이터 파일에서 아직 처리되지 않은 리뷰에 대해 GPT API 호출
- Few-shot 예시와 함께 메시지 구성하여 응답 생성
- 응답에서 <think> 태그의 Reasoning 및 ```json``` 블록의 Answer 추출
- 결과를 CSV 파일로 저장
"""

import os
import re
import json
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
# prompt 모듈에서 프롬프트와 few-shot 예시를 불러옵니다.
from prompt.prompt_loader import load_prompt, load_fewshot

def run_train_data_annotating(config):
    # 환경 변수 로드
    load_dotenv(os.path.expanduser("~/.env"))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인하세요.")
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    # 파일 경로는 config를 통해 읽음
    aste_dir = config["paths"]["aste_dir"]
    train_dir = config["paths"]["train_dir"]
    input_file = os.path.join(aste_dir, "aste_sampled.csv")
    output_temp_file = os.path.join(train_dir, "train_data_TEMP.csv")
    output_final_file = os.path.join(train_dir, "train_data.csv")
    BATCH_SIZE = 10
    MODEL = config["train_data_annotating"]["annotation_model"]

    PROMPT = load_prompt(prompt_filename="annotation_prompt.txt",
                         prompt_dir="./prompt/review_annotation/")
    FEW_SHOT = load_fewshot(fewshot_filename="annotation_fewshot.json",
                            prompt_dir="./prompt/review_annotation/")

    client = OpenAI()

    print("\n[학습 데이터 생성 시작]\n")

    df = pd.read_csv(input_file)
    if os.path.exists(output_temp_file):
        existing = pd.read_csv(output_temp_file)
    else:
        existing = pd.DataFrame()
    processed_ids = set(existing["review-ID"]) if not existing.empty else set()
    remaining = df[~df["review-ID"].isin(processed_ids)].copy()
    print(f"남은 데이터 수: {len(remaining)}\n")

    results = []
    for i in tqdm(range(0, len(remaining), BATCH_SIZE), desc="GPT 처리"):
        batch = remaining.iloc[i : i + BATCH_SIZE]
        for _, row in batch.iterrows():
            messages = [{"role": "system", "content": PROMPT}]
            for example in FEW_SHOT:
                messages.append({"role": "user", "content": example["query"]})
                messages.append({"role": "assistant", "content": example["answer"]})
            messages.append({"role": "user", "content": row["processed"]})
            
            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )
            response = completion.choices[0].message.content
            entry = row.to_dict()
            entry["GPT_Response"] = response
            results.append(entry)
            
        df_batch = pd.DataFrame(results)
        if os.path.exists(output_temp_file):
            df_batch.to_csv(output_temp_file, mode="a", header=False, index=False)
        else:
            df_batch.to_csv(output_temp_file, mode="w", header=True, index=False)
        print(f"처리 완료: {i + len(batch)} / {len(remaining)} 건")
        results = []
    print("\n모든 데이터 GPT 처리 완료.\n")

    df_temp = pd.read_csv(output_temp_file)
    results = []
    for _, row in df_temp.iterrows():
        resp = row.get("GPT_Response", "")
        reasoning = ""
        answer = ""
        try:
            match_think = re.search(r"<think>(.*?)</think>", resp, re.DOTALL)
            if match_think:
                reasoning = match_think.group(1).strip()
        except Exception:
            reasoning = ""
        try:
            match_json = re.search(r"```json\n(.*?)\n```", resp, re.DOTALL)
            if match_json:
                answer = match_json.group(1).strip()
        except Exception:
            answer = ""
        entry = row.copy()
        entry["GPT_Reasoning"] = reasoning
        entry["GPT_Answer"] = answer
        results.append(entry)
    df_final = pd.DataFrame(results)
    df_final.to_csv(output_final_file, index=False)
    
    if os.path.exists(output_temp_file) and (df_temp.shape[0] == df.shape[0]):
        os.remove(output_temp_file)
    
    
    print("[최종 어노테이션 데이터 저장]", output_final_file)

    print("\n[학습 데이터 생성 완료]\n")

if __name__ == "__main__":
    run_train_data_annotating({
        "paths": {
            "data_dir": "./data",
            "prompt_dir": "./prompt"
        },
        "pipeline": {"sft": {"review_annotation": True}}
    })
