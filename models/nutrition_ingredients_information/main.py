import argparse
import yaml
import os
import logging
import subprocess

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

def run_script(script_path):
    """주어진 스크립트를 실행하는 함수"""
    try:
        logging.info(f"Running: {script_path}")
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error while executing {script_path}: {e}")
        exit(1)

# 실행 순서 정의
PIPELINE_ORDER = {
    "preprocessing": ["01_data_selection_323.py", "02_data_selection_273.py"],
    "YOLO": ["01_data_conversion.py", "02_YOLO.py"],
    "OCR": ["01_OCR_text.py", "02_OCR_row_col_323.py", "03_OCR_row_col_273_50.py"],
    "Rule-based": ["01_rule_based.py", "02_eval_nutrition.py"],
    "HCX": ["01_HCX_dataset.py", "02_HCX_train.py", "03_HCX_inference.py", "04_post_processing.py", "05_eval_ingredient.py"]
}

def run_pipeline(pipeline_name, config):
    """해당 파이프라인의 스크립트를 순서대로 실행"""
    logging.info(f"{pipeline_name.upper()} 파이프라인 실행 시작")
    
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", pipeline_name)
    
    for script in PIPELINE_ORDER[pipeline_name]:
        script_path = os.path.join(base_dir, script)
        if os.path.exists(script_path):
            run_script(script_path)
        else:
            logging.warning(f"파일 없음: {script_path} (건너뜀)")
    
    logging.info(f"{pipeline_name.upper()} 파이프라인 완료.")

def main():
    setup_logger()
    parser = argparse.ArgumentParser(description="파이프라인 실행")
    parser.add_argument(
        "--config",
        "-c",
        default="config/config.yaml",
        help="설정 파일 경로 (기본값: config/config.yaml)"
    )
    parser.add_argument(
        "--pipeline",
        "-p",
        choices=["preprocessing", "YOLO", "OCR", "Rule-based", "HCX", "all"],
        default="all",
        help="실행할 파이프라인 선택 (preprocessing, YOLO, OCR, Rule-based, HCX, all)"
    )
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    if args.pipeline in ["preprocessing", "all"]:
        run_pipeline("preprocessing", config)
    if args.pipeline in ["YOLO", "all"]:
        run_pipeline("YOLO", config)
    if args.pipeline in ["OCR", "all"]:
        run_pipeline("OCR", config)
    if args.pipeline in ["Rule-based", "all"]:
        run_pipeline("Rule-based", config)
    if args.pipeline in ["HCX", "all"]:
        run_pipeline("HCX", config)

if __name__ == "__main__":
    main()
