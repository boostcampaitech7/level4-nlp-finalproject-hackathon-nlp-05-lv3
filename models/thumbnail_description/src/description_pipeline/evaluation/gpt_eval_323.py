from utils.common_utils import (
    set_seed, requests, pd, time
)
import yaml
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed

def main():
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 2) OpenAI API Key 설정
    openai.api_key = config["openai"]["api_key"]

    # 3) CSV 파일 경로 설정
    data_dir = config["paths"]["data_dir"]
    qwen2_5_janus_323_eval_path = os.path.join(data_dir, config["paths"]["qwen2_5+janus_323_eval"])
    output_csv = "outputs/gpt_eval_result_janus+qwen2_5.csv"  # 결과 저장용 CSV 파일명

    # 4) CSV 파일 로드
    df = pd.read_csv(qwen2_5_janus_323_eval_path)
    print("Data loaded:", df.shape)

    ### GPT 평가 로직 ###

    def calculate_total_score_from_gpt_eval(eval_text):
        """
        GPT가 생성한 평가 텍스트에서 '평가: x/5' 형태로 된 숫자를 찾아 
        합산한 값을 반환 (10개 항목 * 0~5점).
        """
        try:
            pattern = r"평가:\s*([\d\.]+)/5"
            matches = re.findall(pattern, eval_text)
            scores = [float(m) for m in matches]
            return sum(scores)
        except Exception as e:
            print(f"Error calculating total score: {e}")
            return None

    def evaluate_gpt(model_name, idx, row):
        model_output = row.get("Model Output", "")
        prompt = f"""
        이미지 캡셔닝 결과:
        {model_output}

        위 정보는 원본 이미지와 이에 대한 VLM 모델의 이미지 캡셔닝 결과입니다. 
        아래 항목들을 기준으로 캡션의 품질을 평가하고, 각 항목에 대해 점수(0-5점)를 부여한 후 
        간결하고 명확한 피드백을 제공해주세요.

        평가 항목:
        1.포장 용기의 모양을 명확히 설명했는가? (예: 직사각형, 원형, 비닐형, 정사각형 등)
        2.포장 재질이 정확히 표현되었는가? (예: 종이, 플라스틱, 비닐, 페트병, 캔, 유리 등)
        3.내용물에 대한 정보가 명확히 제시되었는가? (예: 과자, 생선, 과일 등)
        4.패키지에 대한 묘사가 이뤄졌는가?
        5.색상에 대한 설명이 포함되었는가? (예: 빨간색 뚜껑, 투명한 병, 초록색 포장지 등)
        6.제품에 대한 추가 정보를 제공하는가? (해당 제품에 대한 설명이 담겨 있는지)
        7.제품의 실제 특성을 정확히 묘사했는가? (오타나 왜곡된 정보가 없는지)
        8.캡션이 불필요하게 길지 않고, 핵심 정보에 집중했는가?
        9.시각장애인이 쉽게 이해할 수 있도록 명확하고 직관적으로 작성되었는가?
        10.특정 정보를 중복하지 않고, 필요하거나 새로운 정보 위주로 정리되었는가?

        점수 기준(0~5점):
        0점: 전혀 반영되지 않음
        1점: 매우 부족하게 반영됨
        2점: 일부 반영되었으나 부족함
        3점: 보통 수준으로 반영됨
        4점: 대부분 잘 반영됨
        5점: 완벽하게 반영됨

        출력 형식 예시:
        항목: 1.캡션이 포장 용기의 모양을 명확히 설명했는가?
        평가: 4/5
        피드백: 모양이 대부분 명확하게 묘사되었으나, 약간의 세부 정보가 부족함.
        (마지막에 각 항목 점수 합계를 '평가: x/5' 형태로 표기해주세요.)
        """
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o",  
                messages=[
                    {"role": "system", "content": "당신은 VLM의 이미지 캡셔닝 결과를 평가하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1024
            )
            gpt_eval = completion.choices[0].message.content
            return idx, gpt_eval
        except Exception as e:
            print(f"Error for idx {idx}: {e}")
            return idx, None

    def run_tasks(df_input, model_name):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        futures = {}
        with ThreadPoolExecutor() as executor:
            for i, row in df_input.iterrows():
                futures[executor.submit(evaluate_gpt, model_name, i, row)] = i

            for future in as_completed(futures):
                idx = futures[future]
                res = future.result()
                if res is not None:
                    row_idx, gpt_eval_text = res
                    if gpt_eval_text:
                        df_input.at[row_idx, f'Eval ({model_name})'] = gpt_eval_text
                        df_input.at[row_idx, f'Score ({model_name})'] = calculate_total_score_from_gpt_eval(gpt_eval_text)
        return df_input

    # 5) GPT 평가 실행
    model_name = "gpt-4o"
    df_eval = run_tasks(df, model_name)

    # 6) 결과 CSV 저장
    df_eval.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[Info] GPT Evaluation completed and saved => {output_csv}")

    # 7) 그래프 생성용 점수 준비
    # 점수 합 계산
    sum_score = df_eval[f'Score ({model_name})'].sum()
    print(f"Total Score (gpt-4o) = {sum_score}")

    # 모델명 리스트와 점수 리스트
    models = ['Janus_Qwen2_5']

    # 예: 10개 항목 * 5점 만점 * N개 데이터 = 10*N*5 => 최대치
    max_possible_score = 10 * df_eval.shape[0] * 5 
    # 점수 % 계산
    percentage = (sum_score / max_possible_score) * 100
    scores_gpt_4o = [percentage]

    # 그래프
    colors = ['#FF7F50']

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(models, scores_gpt_4o, color=colors, width=0.6)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f} %',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Total Score (%)', fontsize=14, fontweight='bold')
    ax.set_title('Model Performance Comparison (GPT-4o)', fontsize=18, fontweight='bold', pad=20)
    ax.set_ylim(0, max(scores_gpt_4o) * 1.2 if len(scores_gpt_4o) > 0 else 100)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=0, ha='center', fontsize=12, fontweight='bold')
    plt.yticks(fontsize=10)

    for bar in bars:
        bar.set_edgecolor('white')
        bar.set_linewidth(2)

    plt.tight_layout()
    plt.savefig('model_performance_comparison_total.png', dpi=300, bbox_inches='tight')
    print("[Info] Bar chart saved => model_performance_comparison_total.png")

if __name__ == "__main__":
    main()