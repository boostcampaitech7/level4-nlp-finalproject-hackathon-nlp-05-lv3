import os
import logging
import pandas as pd
from utils.hcx import CompletionExecutor
from utils.data_processing import product_introduction_processing

logger = logging.getLogger(__name__)


def run_fewshot_inference(config):
    """
    few-shot 학습 방식으로 HCX-003 모델에 인퍼런스를 수행하고,
    결과를 CSV로 저장한다.
    """
    data_dir = config["paths"]["data_dir"]
    prompt_dir = config["paths"]["prompt_dir"]
    host = config["api"]["host"]
    api_key = config["api"]["api_key"]
    request_id = config["api"]["request_id"]

    total_text_csv = config["paths"]["total_text_csv"]
    fewshot_csv = config["paths"]["fewshot_csv"]
    output_fewshot_csv = config["paths"]["output_fewshot_csv"]

    # Executor 초기화
    completion_executor = CompletionExecutor(
        host=host,
        api_key=api_key,
        request_id=request_id
    )

    # 데이터 불러오기
    data_path = os.path.join(data_dir, total_text_csv)
    data = pd.read_csv(data_path)

    # 전처리
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

        request_data = {
            'messages': messages,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 1024,
            'temperature': 0.5,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 42
        }

        model_output, elapsed_time = completion_executor.execute(request_data)
        data.loc[idx, "summary"] = model_output
        data.loc[idx, "latency"] = elapsed_time
        logger.info(f"[Fewshot Inference] idx={idx}, latency={round(elapsed_time,2)} sec, output={model_output}")

    # 결과 저장
    output_path = os.path.join(data_dir, output_fewshot_csv)
    data.to_csv(output_path, index=False)
    logger.info(f"Few-shot 인퍼런스 결과가 {output_path} 에 저장되었습니다.")
