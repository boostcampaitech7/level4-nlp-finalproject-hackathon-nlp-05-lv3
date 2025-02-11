import argparse
import yaml
import logging

# SFT 파이프라인 모듈 import
from src.sft_pipeline import (
    detailed_feature_description,
    janus_pro_7b_finetuning
)

# Description 파이프라인 내 모델 추론 모듈 import
from src.description_pipeline.inference_model import (
    deepseekvl,
    janus_pro,
    maal,
    qwen2_vl,
    qwen2_5_vl,
    unsloth_qwen2_vl,
    finetuned_janus_pro
)
# Description 파이프라인 내 후처리 모듈 import
from src.description_pipeline.post_processing import (
    janus_pro_papago_translation,
    janus_pro_hcx_translation,
    janus_pro_pp_hcx,
    qwen2_5_pp_hcx
)
# Description 파이프라인 내 평가 모듈 import
from src.description_pipeline.evaluation import (
    gpt_eval,
    gpt_eval_323
)

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

def run_sft_pipeline(config):
    logging.info("SFT 파이프라인 시작")
    # config.yaml에서 sft 파이프라인 관련 설정은 pipeline > sft_pipeline 에 위치함
    sft_config = config.get("pipeline", {}).get("sft_pipeline", {})
    if sft_config.get("detailed_feature_description", False):
        detailed_feature_description.run_detailed_feature_description(config)
    if sft_config.get("janus_pro_7b_finetuning", False):
        janus_pro_7b_finetuning.run_janus_pro_7b_finetuning(config)
    logging.info("SFT 파이프라인 완료.")

def run_description_pipeline(config):
    logging.info("Description 파이프라인 시작")
    # config.yaml에서 description 관련 설정은 pipeline > description_pipeline 에 위치함
    desc_config = config.get("pipeline", {}).get("description_pipeline", {})

    # 1) 모델별 Inference 단계
    inference_cfg = desc_config.get("inference_model", {})
    if inference_cfg.get("deepseekvl", False):
        deepseekvl.run_inference(config)
    if inference_cfg.get("janus_pro", False):
        janus_pro.run_inference(config)
    if inference_cfg.get("maal", False):
        maal.run_inference(config)
    if inference_cfg.get("qwen2_vl", False):
        qwen2_vl.run_inference(config)
    if inference_cfg.get("qwen2_5_vl", False):
        qwen2_5_vl.run_inference(config)
    if inference_cfg.get("unsloth_qwen2_vl", False):
        unsloth_qwen2_vl.run_inference(config)
    if inference_cfg.get("finetuned_janus_pro", False):
        finetuned_janus_pro.run_inference(config)

    # 2) 후처리 단계
    postproc_cfg = desc_config.get("post_processing", {})
    if postproc_cfg.get("janus_pro_papago_translation", False):
        janus_pro_papago_translation.run_post_processing(config)
    if postproc_cfg.get("janus_pro_hcx_translation", False):
        janus_pro_hcx_translation.run_post_processing(config)
    if postproc_cfg.get("janus_pro_pp_hcx", False):
        janus_pro_pp_hcx.run_post_processing(config)
    if postproc_cfg.get("qwen2_5_pp_hcx", False):
        qwen2_5_pp_hcx.run_post_processing(config)

    # 3) Evaluation 단계
    eval_cfg = desc_config.get("evaluation", {})
    if eval_cfg.get("gpt_eval", False):
        gpt_eval.run_evaluation(config)
    if eval_cfg.get("gpt_eval_323", False):
        gpt_eval_323.run_evaluation(config)

    logging.info("Description 파이프라인 완료.")

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
        choices=["sft", "description", "all"],
        default="all",
        help="실행할 파이프라인 선택 (sft, description, all)"
    )
    args = parser.parse_args()

    # 설정 파일 로드
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 선택한 파이프라인 실행
    if args.pipeline in ["sft", "all"]:
        run_sft_pipeline(config)

    if args.pipeline in ["description", "all"]:
        run_description_pipeline(config)

    logging.info("All pipeline tasks completed.")

if __name__ == "__main__":
    main()