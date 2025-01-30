# 상품 설명 요약
> 본 상품 설명 요약 기능에서는 시각장애인 구매자를 위해, 판매자가 작성한 상품 설명 중 핵심 정보를 간결하게 요약합니다.
> 이를 통해 시각장애인 구매자는 상품의 주요 특징, 주의사항 등을 보다 빠르고 쉽게 파악할 수 있습니다.


## 주요 특징
1. **상품 설명 크롤링**: Selenium + BeautifulSoup을 이용해 온라인 쇼핑몰 페이지에서 상품 상세 설명을 수집합니다.
1. **Few-shot Inference**: HyperCLOVA HCX-003 모델을 Few-shot 방식으로 사용하여 간단히 요약을 테스트합니다.
1. **파인튜닝 데이터 생성**: OpenAI GPT-4o 모델을 활용해 대량의 파인튜닝 학습 데이터를 생성합니다.
2. **HCX 모델 파인튜닝**: 생성된 학습 데이터로 HCX-003 모델을 파인튜닝하여 정교한 요약 성능을 얻습니다.
3. **파인튜닝 모델 인퍼런스**: 파인튜닝된 모델을 통해 상품 설명을 빠르게 요약해 냅니다.

> [Note] Few-shot 모델 결과도 확인해볼 수 있지만, 최종 인퍼런스에는 파인튜닝된 모델이 사용됩니다.


## 폴더 구조
```bash
.
├── README.md
├── main.py                        # 파이프라인 실행 코드
├── config
│   └── config.yaml                # 설정(API Key, 파일 경로, 파이프라인 실행 여부 등)
├── data
│   ├── fewshot_5.csv              # Few-shot 예제 데이터
│   ├── finetuning_candidates.csv  # 파인튜닝용 후보 데이터
│   ├── finetuning_v1.csv          # 파인튜닝용 데이터 (273개)
│   ├── output_fewshot.csv         # Few-shot 추론 결과
│   ├── output_finetuning.csv      # 파인튜닝 모델 추론 결과
│   ├── test.csv                   # 평가용 데이터 (50개)
│   ├── total.csv                  # 전체 데이터셋 (323개)
│   └── total_text.csv             # 크롤링 텍스트가 포함된 전체 데이터 (323개)
├── prompt
│   ├── system_prompt.txt          # 시스템 프롬프트
│   └── user_prompt.txt            # 사용자 프롬프트
├── src
│   ├── text_crawling.py               # 상품 상세페이지 텍스트 크롤링
│   ├── fewshot_inference.py           # Few-shot 추론
│   ├── finetuning_data_generation.py  # 파인튜닝용 데이터 생성(OpenAI GPT-4o 모델)
│   ├── create_finetuning_task.py      # HCX 파인튜닝 태스크 생성
│   ├── finetuning_inference.py        # 파인튜닝 모델로 요약 인퍼런스
│   └── result_analysis.py             # 결과 분석 코드
└── utils
    ├── __init__.py
    ├── data_processing.py        # 텍스트 전처리 함수
    └── hcx.py                    # HYPERCLOVA X API 호출용 클래스
```


## 설치 및 실행 방법
### 1) 환경 구축
- Python 3.10.15 버전 권장
- 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 2) 설정
- `config/config.yaml` 파일에서 다음 정보를 적절히 설정합니다.
    - **API Key / Request ID**: HyperCLOVA X 인증 정보
    - **OpenAI API Key**: GPT 모델 사용 시 필요
    - **파일 경로**: 데이터 파일 위치, 파인튜닝 결과 저장 경로 등
    - **파이프라인 실행 여부**: `pipeline` 섹션의 `true`/`false` 값으로 크롤링/인퍼런스/파인튜닝 등 단계별 실행 제어
    - **파인튜닝 설정**: `task_id`, `train_epoch`, `learning_rate` 등 파인튜닝 관련 변수

### 3) 실행
- 기본 실행 (기본 `config/config.yaml` 사용 시)
```bash
python main.py
```
- 별도 설정파일 사용
```bash
python main.py --config config/config_name.yaml
```


## Input & Output
### 1. Input:
- `total.csv`, `total_text.csv`: 상품 URL, 텍스트 등 정보가 들어있는 csv
- `fewshot_5.csv`: Few-shot 테스트용 예시 데이터
- `finetuning_candidates.csv`: 파인튜닝에 활용될 후보 데이터 목록
- `prompt/*`: 시스템 및 사용자 프롬프트 템플릿

### 2. Output
- `finetuning_v1.csv`: GPT-4o로 생성한 파인튜닝용 데이터
- `output_fewshot.csv`: Few-shot 인퍼런스 결과
- `output_finetuning.csv`: 파인튜닝 모델 인퍼런스 결과




## 코드 설명
- `main.py`
    - 파이프라인의 진입점으로, `--config` 인자를 통해 설정 파일(.yaml) 경로를 지정 가능
    - `config.yaml`에서 `pipeline` 섹션의 `true`/`false` 값에 따라 순서대로 `[크롤링 → Few-shot 인퍼런스 → 파인튜닝 데이터 생성 → Task 생성 → 파인튜닝 인퍼런스]` 수행
- `src/text_crawling.py`
    - Selenium + BeautifulSoup을 사용해 상품 상세 URL에서 텍스트를 수집
    - 크롤링 성공 시 `텍스트` 컬럼에 JSON 형식으로 저장.
- `src/fewshot_inference.py`
    - HyperCLOVA HCX-003 모델을 Few-shot프롬프트를 전달해 요약 결과를 획득
    - `fewshot_5.csv`에 있는 예제(질문/답변)를 첨부하여 모델에 추가 맥락을 부여
- `src/finetuning_data_generation.py`
    - 오픈소스 GPT-4o(OpenAI) API를 사용하여 원하는 요약문 예시를 대량 생성(파인튜닝 용도).
    - 결과를 CSV로 저장(예: `finetuning_v1.csv`).
- `src/create_finetuning_task.py`
    - HyperCLOVA API를 이용해 파인튜닝 Task를 생성
    - 응답으로 받은 Task ID를 이후 인퍼런스 단계에서 사용
- `src/finetuning_inference.py`
    - 파인튜닝이 완료된 HyperCLOVA 모델(Task ID 활용)에 요청하여 최종 요약을 수행
    - 결과를 CSV로 저장
- `utils/hcx.py`
    - HyperCLOVA에 API를 호출하기 위한 클래스(`CompletionExecutor`, `CreateTaskExecutor`, `FinetunedCompletionExecutor`)
    - 요청 반복 시도, 에러 처리 등을 포함.
- `utils/data_processing.py`
    - 크롤링된 텍스트(JSON)에서 상품 소개 문구를 전처리하고 병합
