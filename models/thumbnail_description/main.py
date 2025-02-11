import argparse
import yaml
import logging

# 1) description 폴더 내 모델별 추론 함수
from src.description.deepseekvl import run_inference_deepseekvl
from src.description.janus_pro import run_inference_janus_pro
from src.description.maal import run_inference_maal
from src.description.qwen2_vl import run_inference_qwen2_vl
from src.description.qwen2_5_vl import run_inference_qwen2_5_vl
from src.description.unsloth_qwen2_vl import run_inference_unsloth_qwen2_vl

# 2) post_processing 폴더 내 후처리 스크립트
from src.post_processing.janus_pro_papago_translation import run_inference_janus_pro_papago_translation
from src.post_processing.janus_pro_hcx_translation import run_inference_janus_pro_hcx_translation
from src.post_processing.janus_pro_pp_hcx import run_inference_janus_pro_pp_hcx
from src.post_processing.qwen2_5_pp_hcx import run_inference_qwen2_5_pp_hcx

# 3) evaluation 폴더 내 GPT eval 스크립트
from src.evaluation.gpt_eval import run_gpt_eval
from src.evaluation.gpt_eval_323 import run_gpt_eval_323

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s => %(message)s"
    )

def main():
    parser = argparse.ArgumentParser(description="Pipeline for product text summarization & inference")
    parser.add_argument(
        "--config", "-c",
        default="config/config.yaml",
        help="Path to the configuration YAML file (default: config/config.yaml)"
    )
    args = parser.parse_args()

    setup_logger()

    # config.yaml 로드
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    pipeline_cfg = config.get("pipeline", {})
    postproc_cfg = config.get("post_processing", {})
    eval_cfg = config.get("evaluation", {})  # evaluation 섹션

    # 1) 모델별 Inference 파이프라인
    if pipeline_cfg.get("deepseekvl", False):
        run_inference_deepseekvl()

    if pipeline_cfg.get("janus_pro", False):
        run_inference_janus_pro()

    if pipeline_cfg.get("maal", False):
        run_inference_maal()

    if pipeline_cfg.get("qwen2_vl", False):
        run_inference_qwen2_vl()

    if pipeline_cfg.get("qwen2_5_vl", False):
        run_inference_qwen2_5_vl()

    if pipeline_cfg.get("unsloth_qwen2_vl", False):
        run_inference_unsloth_qwen2_vl()

    # 2) 후처리 단계
    if postproc_cfg.get("janus_pro_papago", False):
        run_inference_janus_pro_papago_translation()

    if postproc_cfg.get("janus_pro_hcx_translation", False):
        run_inference_janus_pro_hcx_translation()

    if postproc_cfg.get("janus_pro_pp_hcx", False):
        run_inference_janus_pro_pp_hcx()

    if postproc_cfg.get("qwen2_5_pp_hcx", False):
        run_inference_qwen2_5_pp_hcx()

    # 3) evaluation 단계
    if eval_cfg.get("gpt_eval", False):
        run_gpt_eval()

    if eval_cfg.get("gpt_eval_323", False):
        run_gpt_eval_323()

    logging.info("All pipeline tasks completed.")

if __name__ == "__main__":
    main()