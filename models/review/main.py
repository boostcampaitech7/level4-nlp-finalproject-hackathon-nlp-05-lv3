# main.py
import argparse
import yaml
import os
import logging

# 각 파이프라인 모듈 import
from src.review_pipeline import (
    aste_inference,
    review_summarization,
    keyword_recommendation
)
from src.sft_pipeline import (  
    review_crawling,
    review_preprocessing,
    train_data_sampling,
    train_data_annotating,
    sft  # 3.sft.py – 아직 코드 없음
)

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

def run_sft_pipeline(config):
    logging.info("SFT 파이프라인 시작")
    if config["pipeline"]["sft"].get("review_crawling", False):
        review_crawling.run_review_crawling(config)
    if config["pipeline"]["sft"].get("review_preprocessing", False):
        review_preprocessing.run_review_preprocessing(config)
    if config["pipeline"]["sft"].get("train_data_sampling", False):
        train_data_sampling.run_train_data_sampling(config)
    if config["pipeline"]["sft"].get("train_data_annotating", False):
        train_data_annotating.run_train_data_annotating(config)
    if config["pipeline"]["sft"].get("sft", False):
        sft.run_sft(config)
    logging.info("SFT 파이프라인 완료.")

def run_review_pipeline(config):
    logging.info("리뷰 파이프라인 시작")
    # (크롤링은 별도 실행할 경우 config의 crawling 옵션에 따라 실행)
    if config["pipeline"]["review"].get("aste_inference", False):
        aste_inference.run_aste_inference(config)
    if config["pipeline"]["review"].get("review_summarization", False):
        review_summarization.run_review_summarization(config)
    if config["pipeline"]["review"].get("keyword_recommendation", False):
        keyword_recommendation.run_keyword_recommendation(config)
    logging.info("리뷰 파이프라인 완료.")


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
        choices=["review", "sft", "all"],
        default="all",
        help="실행할 파이프라인 선택 (review, sft, all)"
    )
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    if args.pipeline in ["sft", "all"]:
        run_sft_pipeline(config)

    if args.pipeline in ["review", "all"]:
        run_review_pipeline(config)


if __name__ == "__main__":
    main()
