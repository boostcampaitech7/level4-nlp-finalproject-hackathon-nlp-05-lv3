from utils.common_utils import (
    set_seed, requests, pd, time
)
import yaml
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed

import openai

def main():
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 2) OpenAI API 키 설정 
    openai.api_key = config["openai"]["api_key"]

    # 3) CSV 파일 경로 설정
    data_dir = config["paths"]["data_dir"]
    output_csv = "outputs/gpt_eval_result_janus+qwen2_5.csv" 
    
    internvl_eval_path    = os.path.join(data_dir, config["paths"]["internVL_eval"])
    maai_eval_path        = os.path.join(data_dir, config["paths"]["maai_eval"])
    qwen_unsloth_eval_path= os.path.join(data_dir, config["paths"]["unsloth_qwen2_eval"])
    qwen2_eval_path       = os.path.join(data_dir, config["paths"]["qwen2_eval"])
    deepseekvl_eval_path  = os.path.join(data_dir, config["paths"]["deepseekvl_eval"])
    qwen2_5_eval_path     = os.path.join(data_dir, config["paths"]["qwen2.5_eval"])
    janus_eval_path       = os.path.join(data_dir, config["paths"]["janus_pro_eval"])
    qwen2_5_janus_eval_path = os.path.join(data_dir, config["paths"]["qwen2_5+janus_eval"])

    # 4) CSV 로드
    internvl_eng_eval = pd.read_csv(internvl_eval_path)
    maai_eval         = pd.read_csv(maai_eval_path)
    qwen_unsloth_eval = pd.read_csv(qwen_unsloth_eval_path)
    qwen2_eval        = pd.read_csv(qwen2_eval_path)
    deepseekvl_eval   = pd.read_csv(deepseekvl_eval_path)
    qwen2_5_eval      = pd.read_csv(qwen2_5_eval_path)
    janus_eval        = pd.read_csv(janus_eval_path)
    qwen2_5_janus_eval= pd.read_csv(qwen2_5_janus_eval_path)


    # 5) GPT 평가 로직 준비
    def calculate_total_score_from_gpt_eval(eval_text):
        """
        GPT가 반환한 평가 텍스트 내에 '평가: x/5' 형태의 항목을 정규식으로 찾아
        합계를 구하는 함수 (10개 항목 * 0~5점).
        """
        try:
            pattern = r"평가:\s*([\d\.]+)/5"
            scores = [float(match) for match in re.findall(pattern, eval_text)]
            return sum(scores)
        except Exception as e:
            print(f"Error calculating total score: {e}")
            return None

    def evaluate_gpt(row):
        """
        GPT API 호출 함수.
        row: pd.Series 형태 (주어진 CSV 한 행)
        """
        model_output_text = row.get("Model Output", "")
        prompt = f"""
        이미지 캡셔닝 결과:
        {model_output_text}

        위 정보는 원본 이미지와 이에 대한 VLM 모델의 이미지 캡셔닝 결과입니다. 아래 항목들을 기준으로 캡션의 품질을 평가하고, 각 항목에 대해 점수(0-5점)를 부여한 후 간결하고 명확한 피드백을 제공해주세요.

        평가 항목:
        1.포장 용기의 모양을 명확히 설명했는가? (0~5점)
        2.포장 재질이 정확히 표현되었는가? (0~5점)
        3.내용물에 대한 정보가 명확히 제시되었는가? (0~5점)
        4.색상에 대한 설명이 포함되었는가? (0~5점)
        5.디테일한 묘사가 이뤄졌는가? (0~5점)
        6.제품에 대한 추가 정보를 제공하는가? (0~5점)
        7.제품의 실제 특성을 정확히 묘사했는가? (오타나 왜곡 없는지) (0~5점)
        8.불필요하게 길지 않고, 핵심 정보에 집중했는가? (0~5점)
        9.시각장애인이 쉽게 이해할 수 있도록 직관적으로 작성되었는가? (0~5점)
        10.특정 정보를 중복하지 않고, 새롭거나 필요한 정보 위주로 정리되었는가? (0~5점)

        점수 기준(0~5점):
        0점: 전혀 반영되지 않음
        1점: 매우 부족하게 반영됨
        2점: 일부 반영되었으나 부족함
        3점: 보통 수준으로 반영됨
        4점: 대부분 잘 반영됨
        5점: 완벽하게 반영됨

        출력 예시:
        항목1: 4/5
        피드백: ...
        ...
        (마지막에 '평가: x/5' 형태로 각 항목 점수 합계를 표기해 주세요.)
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": "당신은 이미지 캡셔닝 결과를 평가하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1024
            )
            gpt_eval_text = response.choices[0].message.content
            return gpt_eval_text
        except Exception as e:
            print(f"Error calling GPT: {e}")
            return None

    def run_tasks(df: pd.DataFrame) -> pd.DataFrame:
        """
        ThreadPoolExecutor를 사용해 병렬로 GPT 평가 수행.
        """
        with ThreadPoolExecutor() as executor:
            futures = {}
            for idx, row in df.iterrows():
                futures[executor.submit(evaluate_gpt, row)] = idx

            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                if result is not None:
                    df.at[idx, "Eval (gpt-4o)"] = result
                    df.at[idx, "Score (gpt-4o)"] = calculate_total_score_from_gpt_eval(result)
        return df

    # 6) 각 데이터프레임에 대해서 GPT 평가 추가 ("Score (gpt-4o)" 열)
    internvl_eng_eval = run_tasks(internvl_eng_eval)
    maai_eval         = run_tasks(maai_eval)
    deepseekvl_eval   = run_tasks(deepseekvl_eval)
    qwen_unsloth_eval = run_tasks(qwen_unsloth_eval)
    qwen2_eval        = run_tasks(qwen2_eval)
    qwen2_5_eval      = run_tasks(qwen2_5_eval)
    janus_eval        = run_tasks(janus_eval)
    qwen2_5_janus_eval= run_tasks(qwen2_5_janus_eval)

    # 7) CSV로 다시 저장 (원하면 overwrite or new filename)
    internvl_eng_eval.to_csv(internvl_eval_path, index=False, encoding='utf-8-sig')
    maai_eval.to_csv(maai_eval_path, index=False, encoding='utf-8-sig')
    deepseekvl_eval.to_csv(deepseekvl_eval_path, index=False, encoding='utf-8-sig')
    qwen_unsloth_eval.to_csv(qwen_unsloth_eval_path, index=False, encoding='utf-8-sig')
    qwen2_eval.to_csv(qwen2_eval_path, index=False, encoding='utf-8-sig')
    qwen2_5_eval.to_csv(qwen2_5_eval_path, index=False, encoding='utf-8-sig')
    janus_eval.to_csv(janus_eval_path, index=False, encoding='utf-8-sig')
    qwen2_5_janus_eval.to_csv(qwen2_5_janus_eval_path, index=False, encoding='utf-8-sig')

    print("[Info] GPT-4o Evaluation columns added to each CSV successfully.")

    # 8) 모델별 점수 합 계산
    internvl_eng_total_score_gpt_4o = internvl_eng_eval['Score (gpt-4o)'].sum()
    maai_total_score_gpt_4o         = maai_eval['Score (gpt-4o)'].sum()
    deepseekvl_total_score_gpt_4o   = deepseekvl_eval['Score (gpt-4o)'].sum()
    qwen2_unsloth_total_score_gpt_4o= qwen_unsloth_eval['Score (gpt-4o)'].sum()
    qwen2_total_score_gpt_4o        = qwen2_eval['Score (gpt-4o)'].sum()
    qwen2_5_total_score_gpt_4o      = qwen2_5_eval['Score (gpt-4o)'].sum()
    janus_total_score_gpt_4o        = janus_eval['Score (gpt-4o)'].sum()
    qwen2_5_janus_total_score_gpt_4o= qwen2_5_janus_eval['Score (gpt-4o)'].sum()

    print(f"internvl_eng Score (gpt-4o): {internvl_eng_total_score_gpt_4o}")
    print(f"maai Score (gpt-4o): {maai_total_score_gpt_4o}")
    print(f"deepseekvl Score (gpt-4o): {deepseekvl_total_score_gpt_4o}")
    print(f"qwen2_unsloth Score (gpt-4o): {qwen2_unsloth_total_score_gpt_4o}")
    print(f"qwen2 Score (gpt-4o): {qwen2_total_score_gpt_4o}")
    print(f"qwen2_5 Score (gpt-4o): {qwen2_5_total_score_gpt_4o}")
    print(f"janus Score (gpt-4o): {janus_total_score_gpt_4o}")
    print(f"qwen2_5_janus Score (gpt-4o): {qwen2_5_janus_total_score_gpt_4o}")

    # 9) 평균 추론 시간 계산
    internvl_eng_avg_time = internvl_eng_eval['Inference Time (s)'].mean()
    maai_avg_time         = maai_eval['Inference Time (s)'].mean()
    deepseekvl_avg_time   = deepseekvl_eval['Inference Time (s)'].mean()
    qwen2_unsloth_avg_time= qwen_unsloth_eval['Inference Time (s)'].mean()
    qwen2_avg_time        = qwen2_eval['Inference Time (s)'].mean()
    qwen2_5_avg_time      = qwen2_5_eval['Inference Time (s)'].mean()
    janus_avg_time        = janus_eval['Inference Time (s)'].mean()
    qwen2_5_janus_avg_time= qwen2_5_janus_eval['Inference Time (s)'].mean()

    print(f"internvl Avg Inference Time: {internvl_eng_avg_time:.2f}")
    print(f"maai Avg Inference Time: {maai_avg_time:.2f}")
    print(f"deepseekvl Avg Inference Time: {deepseekvl_avg_time:.2f}")
    print(f"qwen2(unsloth) Avg Inference Time: {qwen2_unsloth_avg_time:.2f}")
    print(f"qwen2 Avg Inference Time: {qwen2_avg_time:.2f}")
    print(f"qwen2_5 Avg Inference Time: {qwen2_5_avg_time:.2f}")
    print(f"janus Avg Inference Time: {janus_avg_time:.2f}")
    print(f"qwen2_5_janus Avg Inference Time: {qwen2_5_janus_avg_time:.2f}")

    # 10) 시각화 파트 
    # Performance Comparison
    models = ['MAAI','InternVL','Qwen2_VL(Unsloth)','Qwen2_VL','DeepSeek_VL','Qwen2_5_VL','Janus_Pro','Qwen2_5_Janus' ]
    total_scores_gpt_4o = [
        maai_total_score_gpt_4o,
        internvl_eng_total_score_gpt_4o,
        qwen2_unsloth_total_score_gpt_4o,
        qwen2_total_score_gpt_4o,
        deepseekvl_total_score_gpt_4o,
        qwen2_5_total_score_gpt_4o,
        janus_total_score_gpt_4o,
        qwen2_5_janus_total_score_gpt_4o
    ]
    # 10개 항목 * 5점 만점 * N개 데이터?? 예: 50개, => 2500점 = 100%  
    total_scores_gpt_4o_percent = [(val / 2500) * 100 for val in total_scores_gpt_4o]

    colors = ['#FF7F50', '#008080', '#E6E6FA', '#FFD700', '#DDA0DD', '#6A5ACD', '#32CD32', '#DC143C']
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(models, total_scores_gpt_4o_percent, color=colors, width=0.6)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h,
                f'{h:.2f} %',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Score (%)', fontsize=14, fontweight='bold')
    ax.set_title('Model Performance Comparison (gpt-4o)', fontsize=18, fontweight='bold', pad=20)
    ax.set_ylim(0, max(total_scores_gpt_4o_percent) * 1.2)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=0, ha='center', fontsize=12, fontweight='bold')
    plt.yticks(fontsize=10)
    for bar in bars:
        bar.set_edgecolor('white')
        bar.set_linewidth(2)
    plt.tight_layout()
    plt.savefig('model_performance_comparison_8.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Inference Time Comparison
    avg_times = [
        maai_avg_time,
        internvl_eng_avg_time,
        qwen2_unsloth_avg_time,
        qwen2_avg_time,
        deepseekvl_avg_time,
        qwen2_5_avg_time,
        janus_avg_time,
        qwen2_5_janus_avg_time
    ]
    fig2, ax2 = plt.subplots(figsize=(12, 8))
    bars2 = ax2.bar(models, avg_times, color=colors, width=0.6)
    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., h,
                 f'{h:.2f} (s)',
                 ha='center', va='bottom', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Avg Inference Time (s)', fontsize=14, fontweight='bold')
    ax2.set_title('Model Avg Inference Time Comparison', fontsize=18, fontweight='bold', pad=20)
    ax2.set_ylim(0, max(avg_times) * 1.2)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=0, ha='center', fontsize=12, fontweight='bold')
    plt.yticks(fontsize=10)
    for bar in bars2:
        bar.set_edgecolor('white')
        bar.set_linewidth(2)
    plt.tight_layout()
    plt.savefig('model_avg_inference_time_comparison_8.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()