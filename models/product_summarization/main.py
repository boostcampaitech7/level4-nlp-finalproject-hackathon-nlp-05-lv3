import yaml
import logging
import argparse
from src.text_crawling import run_text_crawling
from src.fewshot_inference import run_fewshot_inference
from src.finetuning_data_generation import run_finetuning_data_generation
from src.create_finetuning_task import run_create_finetuning_task
from src.finetuning_inference import run_finetuning_inference

def setup_logger():
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    

def main():
    
    # 파라미터 파싱
    parser = argparse.ArgumentParser(description="Pipeline for product text summarization.")
    parser.add_argument(
        "--config",
        "-c",
        default="config/config.yaml",
        help="Path to the configuration YAML file (default: config/config.yaml)"
    )
    args = parser.parse_args()
    
    # 로거 설정
    setup_logger()

    # config 불러오기
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 단계별 실행
    if config["pipeline"].get("text_crawling", False):
        run_text_crawling(config)

    if config["pipeline"].get("fewshot_inference", False):
        run_fewshot_inference(config)

    if config["pipeline"].get("finetuning_data_generation", False):
        run_finetuning_data_generation(config)

    if config["pipeline"].get("create_finetuning_task", False):
        run_create_finetuning_task(config)

    if config["pipeline"].get("finetuning_inference", False):
        run_finetuning_inference(config)

if __name__ == "__main__":
    main()
