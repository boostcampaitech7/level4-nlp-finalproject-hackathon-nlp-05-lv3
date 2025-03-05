import logging
from utils.hcx import CreateTaskExecutor

logger = logging.getLogger(__name__)


def run_create_finetuning_task(config):
    """
    HCX 파인튜닝 Task를 생성하고, 생성된 Task ID를 로그로 남긴다.
    """
    host = config["api"]["host"]
    uri = config["finetuning"]["uri"]
    api_key = config["api"]["api_key"]
    request_id = config["api"]["request_id"]

    # 요청 데이터 구성
    request_data = {
        'name': config["finetuning"]["new_task_name"],
        'model': config["finetuning"]["model"],
        'tuningType': config["finetuning"]["tuning_type"],
        'taskType': config["finetuning"]["task_type"],
        'trainEpochs': str(config["finetuning"]["train_epochs"]),
        'learningRate': config["finetuning"]["learning_rate"],
        'trainingDatasetBucket': config["finetuning"]["dataset_bucket"],
        'trainingDatasetFilePath': config["finetuning"]["dataset_file_path"],
        'trainingDatasetAccessKey': config["finetuning"]["dataset_access_key"],
        'trainingDatasetSecretKey': config["finetuning"]["dataset_secret_key"]
    }

    create_task_executor = CreateTaskExecutor(
        host=host,
        uri=uri,
        api_key=api_key,
        request_id=request_id
    )

    response_text = create_task_executor.execute(request_data)
    logger.info(f"Create Finetuning Task Response: {response_text}")
    
    if isinstance(response_text, dict) and "id" in response_text:
        logger.info(f"Created new tuning Task ID: {response_text['id']}")
    else:
        logger.error("Failed to create new tuning task.")
