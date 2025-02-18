import os
import logging
import pandas as pd
from openai import OpenAI
from utils.data_processing import product_introduction_processing

logger = logging.getLogger(__name__)


def run_finetuning_data_generation(config):
    """
    OpenAI의 GPT-4o 모델을 사용하여 
    파인튜닝용 데이터 생성 및 CSV 저장.
    """
    # OpenAI API 설정
    os.environ["OPENAI_API_KEY"] = config["openai"]["api_key"]
    client = OpenAI()

    data_dir = config["paths"]["data_dir"]
    prompt_dir = config["paths"]["prompt_dir"]
    fewshot_csv = config["paths"]["fewshot_csv"]
    finetuning_candidates_csv = config["paths"]["finetuning_candidates_csv"]
    finetuning_csv = config["paths"]["finetuning_csv"]

    # 데이터 불러오기
    candidates_path = os.path.join(data_dir, finetuning_candidates_csv)
    data = pd.read_csv(candidates_path)
    data['상품소개'] = data.apply(product_introduction_processing, axis=1)

    # 프롬프트 불러오기
    with open(os.path.join(prompt_dir, "system_prompt.txt"), "r", encoding="utf-8") as f:
        system_prompt = f.read()
    with open(os.path.join(prompt_dir, "user_prompt.txt"), "r", encoding="utf-8") as f:
        user_prompt = f.read()

    # fewshot 데이터 불러오기
    fewshot_data = pd.read_csv(os.path.join(data_dir, fewshot_csv))
    fewshot_message = []
    for idx, row in fewshot_data.iterrows():
        fewshot_prompt = user_prompt.replace("{product_name}", row['상품명']) \
                                   .replace("{product_introduction}", row["상품소개"])
        fewshot_answer = row['요약']
        fewshot_message.append({"role": "user", "content": fewshot_prompt})
        fewshot_message.append({"role": "assistant", "content": fewshot_answer})

    # 인퍼런스
    for idx, row in data.iterrows():
        prompt_replaced = user_prompt.replace("{product_name}", row['상품명']) \
                                     .replace("{product_introduction}", row['상품소개'])
        messages = [{"role": "system", "content": system_prompt}] + fewshot_message + \
                   [{"role": "user", "content": prompt_replaced}]

        # 상품 설명 문구 생성
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"}
        )

        result = completion.choices[0].message.content
        data.loc[idx, "Text"] = prompt_replaced
        data.loc[idx, "Completion"] = result
        logger.info(f"[Finetuning Data Gen] idx={idx}, product={row['상품명']}, result={result}")

    # 파인튜닝 데이터 형태로 정제
    final_df = data.copy()
    final_df['System_Prompt'] = system_prompt 
    final_df['C_ID'] = list(range(len(final_df)))
    final_df['T_ID'] = 0
    final_df = final_df[['System_Prompt', 'C_ID', 'T_ID', 'Text', 'Completion']]
    
    # CSV 저장
    output_path = os.path.join(data_dir, finetuning_csv)
    final_df.to_csv(output_path, index=False)
    logger.info(f"파인튜닝용 데이터가 {output_path} 에 저장되었습니다.")

