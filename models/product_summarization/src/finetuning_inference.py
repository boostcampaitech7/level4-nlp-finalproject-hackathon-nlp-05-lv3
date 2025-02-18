import os
import logging
import pandas as pd
from utils.hcx import FinetunedCompletionExecutor
from utils.data_processing import product_introduction_processing

logger = logging.getLogger(__name__)


def run_finetuning_inference(config):
    """
    파인튜닝된 모델(이미 생성된 Task ID 활용)로 인퍼런스를 수행하고,
    결과를 CSV로 저장한다.
    """
    data_dir = config["paths"]["data_dir"]
    prompt_dir = config["paths"]["prompt_dir"]
    host = config["api"]["host"]
    api_key = config["api"]["api_key"]
    request_id = config["api"]["request_id"]
    task_id = config["finetuning"]["task_id"]
    
    total_text_csv = config["paths"]["total_text_csv"]
    output_finetuning_csv = config["paths"]["output_finetuning_csv"]

    # 데이터 불러오기
    data_path = os.path.join(data_dir, total_text_csv)
    
    data = pd.read_csv(data_path)
    data['상품소개'] = data.apply(product_introduction_processing, axis=1)

    # 프롬프트 불러오기
    with open(os.path.join(prompt_dir, "system_prompt.txt"), "r", encoding="utf-8") as f:
        system_prompt = f.read()
    with open(os.path.join(prompt_dir, "user_prompt.txt"), "r", encoding="utf-8") as f:
        user_prompt = f.read()

    # 파인튜닝된 모델 Executor
    finetuned_completion_executor = FinetunedCompletionExecutor(
        host=host,
        api_key=api_key,
        request_id=request_id,
        taskId=task_id
    )

    # 인퍼런스
    for idx, row in data.iterrows():
        prompt_replaced = user_prompt.replace("{product_name}", row['상품명']) \
                                     .replace("{product_introduction}", row['상품소개'])

        request_data = {
            'messages': [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_replaced}
            ],
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 1024,
            'temperature': 0.5,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 42
        }

        model_output, elapsed_time = finetuned_completion_executor.execute(request_data)
        data.loc[idx, "summary"] = model_output
        data.loc[idx, "latency"] = elapsed_time
        logger.info(f"[Finetuning Inference] idx={idx}, latency={round(elapsed_time,2)} sec, output={model_output}")

    # 결과 저장
    output_path = os.path.join(data_dir, output_finetuning_csv)
    data.to_csv(output_path, index=False)
    logger.info(f"파인튜닝 모델 인퍼런스 결과가 {output_path} 에 저장되었습니다.")
