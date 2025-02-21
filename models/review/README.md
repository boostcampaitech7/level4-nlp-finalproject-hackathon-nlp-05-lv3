"""
# 리뷰 파이프라인
> 본 리뷰 파이프라인은 리뷰 데이터를 정제 및 요약하여, 사용자가 상품 리뷰를 효과적으로 이해하고, 추천 키워드를 통해 상품 검색 및 정렬 기능을 제공하는 것을 목표로 합니다.  
> 파이프라인은 두 개의 주요 모듈로 구성되어 있습니다:  
> 1. **학습 데이터 생성 파이프라인** (ASTE Task용 데이터 생성 및 모델 파인튜닝)  
> 2. **추천 키워드 검색과 리뷰 요약 파이프라인** (ASTE 인퍼런스, 임베딩, 클러스터링 및 후처리)

## 주요 특징
1. **리뷰 크롤링 및 전처리**:  
   온라인 쇼핑몰에서 상품 정보 및 리뷰를 수집한 후, 텍스트 클렌징, 특수문자 제거, 개행 문자 변환, 영어/숫자 비율 필터링, 중복 제거, 짧은 리뷰 배제, 맞춤법 교정 등 다양한 전처리 과정을 수행합니다.
2. **ASTE(Aspect Sentiment Triplet Extraction) 데이터 생성**:  
   전처리된 리뷰 데이터를 바탕으로 Sentence-BERT 임베딩과 K-Means 클러스터링을 활용하여 중복을 방지한 대표 리뷰 샘플을 선택하고, GPT API를 통해 ASTE 관련 900개의 학습 데이터를 생성합니다.
3. **모델 파인튜닝**:  
   'DeepSeek-R1-Distill-Qwen' 모델을 기반으로 Supervised Fine-Tuning(SFT)을 진행하여, 리뷰의 Aspect, Opinion, Sentiment 추출 능력을 향상시킵니다. 100개의 수동 레이블링 데이터와 Custom Evaluation Metric을 이용하여 정량적으로 모델의 성능 평가를 실시합니다.
4. **추천 키워드 및 리뷰 요약**:  
   파인튜닝된 ASTE 모델의 인퍼런스 결과를 Sentence-BERT 임베딩과 UMAP 차원 축소, Agglomerative 클러스터링으로 분석하여 HyperClovaX로 대표 키워드를 도출하고, 긍정/부정 리뷰 요약을 생성합니다.
5. **클러스터링 평가 및 시각화**:  
   T-SNE를 활용한 시각화와 Silhouette, DBI 등의 평가 지표를 통해 클러스터링 결과의 품질을 정량적으로 분석합니다.

> [Note] 학습 데이터 생성과 추천 키워드 검색 및 리뷰 요약은 독립적인 모듈로 구성되어 있으며, 필요에 따라 개별 실행이 가능합니다.

## 폴더 구조
```bash
.
├── README.md
├── main.py                        # 파이프라인 실행 코드
├── config
│   └── config.yaml                # 설정 파일 (파일 경로, 실행 옵션 등)
├── data
│   ├── ASTE
│   │   ├── ASTE_10_shots.csv              # 10-shot 예제 데이터
│   │   ├── ASTE_sampled.csv               # 샘플링된 리뷰 데이터
│   │   ├── eval
│   │   │   └── ASTE_annotation_100_golden_label.csv   # 100개 Golden Label 데이터
│   │   ├── inference
│   │   │   └── deepseek_inference.csv     # DeepSeek 인퍼런스 결과 (모델 출력 포함)
│   │   ├── processed_except_GL.csv          # Golden Label 제외 전처리 리뷰 데이터
│   │   └── train
│   │       └── train_data.csv               # 학습용 리뷰 데이터
│   ├── crawled_reviews
│   │   ├── crawled_reviews_meals.csv       # 라면/간편식 관련 리뷰 크롤링 데이터
│   │   └── crawled_reviews_snacks.csv      # 과자/빙과 관련 리뷰 크롤링 데이터
│   ├── embedding_matrics
│   │   ├── cluster_result.png              # 클러스터링 결과 시각화 이미지
│   │   ├── clustering_evaluation.json      # 클러스터링 평가 지표
│   │   ├── deepseek_inference.npy          # 전체 인퍼런스 임베딩 행렬
│   │   ├── deepseek_inference_meals.npy    # 라면/간편식 리뷰 임베딩 데이터
│   │   ├── deepseek_inference_reduced.npy  # 차원 축소 후 임베딩 데이터
│   │   ├── deepseek_inference_snacks.npy   # 과자/빙과 리뷰 임베딩 데이터
│   │   ├── meals_cluster_result.png
│   │   ├── meals_clustering_evaluation.json
│   │   ├── snacks_cluster_result.png
│   │   └── snacks_clustering_evaluation.json
│   └── preprocessed
│       ├── meta_reviews_meals.csv          # 라면/간편식 리뷰 메타 데이터
│       ├── meta_reviews_snacks.csv         # 과자/빙과 리뷰 메타 데이터
│       ├── processed_reviews_all.csv       # 전체 전처리 리뷰 데이터
│       ├── processed_reviews_meals.csv     # 라면/간편식 리뷰 전처리 결과
│       └── processed_reviews_snacks.csv    # 과자/빙과 리뷰 전처리 결과
├── prompt
│   ├── keyword_recommendation
│   │   ├── recommendation_fewshot.json     # 추천 키워드 Few-shot 예제
│   │   └── recommendation_prompt.txt       # 추천 키워드 프롬프트 템플릿
│   ├── prompt_loader.py                    # 프롬프트 로더 스크립트
│   ├── review_annotation
│   │   ├── annotation_fewshot.json         # 리뷰 어노테이션 Few-shot 예제
│   │   └── annotation_prompt.txt           # 리뷰 어노테이션 프롬프트 템플릿
│   └── review_summarization
│       ├── negative_fewshot.json           # 부정 리뷰 요약 예제
│       ├── negative_prompt.txt             # 부정 리뷰 요약 프롬프트 템플릿
│       ├── positive_fewshot.json           # 긍정 리뷰 요약 예제
│       └── positive_prompt.txt             # 긍정 리뷰 요약 프롬프트 템플릿
├── src
│   ├── review_pipeline
│   │   ├── ASTE_inference.py              # ASTE 모델 인퍼런스 실행(더미 데이터)
│   │   ├── keyword_recommendation.py      # 추천 키워드 추출 및 정렬
│   │   ├── qwen_deepseek_14b_inference.py   # Qwen 14B 기반 인퍼런스
│   │   ├── qwen_deepseek_32b_inference.py   # Qwen 32B 기반 인퍼런스
│   │   ├── review_summarization.py        # 리뷰 요약 추출 실행
│   │   └── visualization.py               # 클러스터링 결과 시각화 및 평가
│   └── sft_pipeline
│       ├── qwen_deepseek_14b_finetuning.py  # Qwen 14B 모델 파인튜닝
│       ├── qwen_deepseek_32b_finetuning.py  # Qwen 32B 모델 파인튜닝
│       ├── review_crawling.py             # 리뷰 데이터 크롤링
│       ├── review_preprocessing.py        # 리뷰 전처리 실행
│       ├── sft.py                         # Supervised Fine-Tuning 실행(더미 데이터)
│       ├── train_data_annotating.py       # 리뷰 어노테이션 데이터 생성
│       └── train_data_sampling.py         # 리뷰 샘플링
├── environment.yml                     # Conda 환경 설정 파일
└── utils
    ├── evaluate.py                     # ASTE 및 클러스터링 평가 코드
    └── utils.py                        # 유틸리티 함수 모음
```

## 설치 및 실행 방법
### 1) 환경 구축
- Python 3.11.11 버전 권장
- 의존성 패키지 설치:
```bash
conda env create -f environment.yml
```

### 2) 설정
- `config/config.yaml` 파일에서 다음 정보를 적절히 설정합니다.
    - **파일 경로**: 데이터 파일 경로 등
    - **파이프라인 실행 여부**: pipeline 섹션의 true/false 값으로 각 단계(크롤링, 전처리, 인퍼런스, 파인튜닝, 추천 등) 실행 제어
    - **학습 데이터 생성 설정**: GPT모델 선택, 학습 데이터 개수 설정 등

### 3) 실행
- 기본 실행 (기본 `config/config.yaml` 사용 시)
```bash
python main.py -p sft
python main.py -p review
```

## Input & Output
### 1. Input:
- 크롤링 데이터:
    - `crawled_reviews/`: 온라인 쇼핑몰에서 크롤링한 원본 리뷰 데이터 (예: `crawled_reviews_meals.csv`, `crawled_reviews_snacks.csv`)
- 전처리 데이터:
    - `preprocessed/`: 전처리된 리뷰 데이터 (`processed_reviews_all.csv`, `processed_reviews_meals.csv`, `processed_reviews_snacks.csv`)
- ASTE 관련 CSV 파일:
    - `aste/`: Golden Label, 샘플링 데이터 등 ASTE 학습 및 인퍼런스에 사용되는 데이터
- 프롬프트 템플릿:
    - `prompt/*`: 추천 키워드, 리뷰 어노테이션 및 요약을 위한 프롬프트 템플릿

### 2. Output:
- 학습 데이터 생성 파이프라인 결과
    - `train_data.csv`: 파인튜닝용 리뷰 학습 데이터
    - `ASTE_sampled.csv`: 클러스터링으로 샘플링된 리뷰 데이터
    - 기타 학습 데이터 생성 결과 CSV (GPT API를 통한 ASTE 데이터 생성 결과)
- 추천 키워드 검색 및 리뷰 요약 파이프라인 결과
    - `deepseek_inference.csv`: ASTE 인퍼런스 결과 (Aspect, Opinion, Sentiment 포함)
- 최종 추천 CSV 파일: 추천 키워드 기반 상품 재정렬 및 리뷰 요약 결과
- 클러스터링 평가 자료 (시각화 이미지, 평가 지표 JSON 등)




## 코드 설명
`main.py`
파이프라인의 진입점으로, config/config.yaml 파일의 설정에 따라 각 단계(크롤링, 전처리, 학습 데이터 생성, SFT, 인퍼런스 등)를 순차적으로 실행합니다.

- `src/review_pipeline/`
    - `ASTE_inference.py`: ASTE 모델 인퍼런스를 수행하여 리뷰에서 (Aspect, Opinion, Sentiment)를 추출합니다.
    - `keyword_recommendation.py`: 인퍼런스 결과를 기반으로 Sentence-BERT 임베딩과 클러스터링을 통해 대표 키워드를 도출하고, 상품 정렬에 활용합니다.
    - `qwen_deepseek_14b_inference.py`, `qwen_deepseek_32b_inference.py`: 다양한 Qwen 기반 모델을 활용한 인퍼런스 실행 코드입니다.
    - `review_summarization.py`: 리뷰의 핵심 포인트를 요약하여 긍정 및 부정 리뷰 요약을 생성합니다.
    - `visualization.py`: T-SNE 시각화 및 클러스터링 평가(실루엣, DBI 등)를 수행합니다.

- `src/sft_pipeline/`
    - `qwen_deepseek_14b_finetuning.py`, `qwen_deepseek_32b_finetuning.py`: 선택된 Qwen 모델에 대해 ASTE Task의 SFT(파인튜닝)를 진행합니다.
    - `review_crawling.py`: 온라인 쇼핑몰에서 상품 정보와 리뷰 데이터를 크롤링합니다.
    - `review_preprocessing.p`y: 크롤링된 리뷰 데이터를 전처리(특수문자 제거, 맞춤법 교정, 중복 제거 등)합니다.
    - `sft.py`: SFT(슈퍼바이즈드 파인튜닝) 실행을 위한 핵심 코드입니다.
    - `train_data_annotating.py`: GPT API를 활용하여 리뷰 어노테이션 데이터를 생성합니다.
    - `train_data_sampling.py`: Sentence-BERT 임베딩과 K-Means 클러스터링을 이용해 대표 리뷰 샘플을 추출합니다.

- `utils/`
    - `evaluate.py`: ASTE 및 클러스터링 평가(정량적 지표 산출)를 수행하는 코드입니다.
    - `utils.py`: 데이터 전처리, 파일 입출력 등 다양한 유틸리티 함수 모음입니다.