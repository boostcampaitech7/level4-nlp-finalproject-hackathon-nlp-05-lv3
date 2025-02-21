# 영양/성분 정보 추출
> 본 기능은 OCR을 활용하여 제품의 영양/성분 정보를 추출하는 기능입니다.
> 판매자가 제공한 영양/성분 정보 이미지를 분석하여 영양정보, 원재료, 알레르기(1차/2차), 보관방법(개봉전/후) 등을 식별합니다.
> 이를 통해 시각장애인도 제품의 영양/성분 정보를 확인하고 안전하게 구매할 수 있도록 지원합니다.


## 주요 특징
1. **OCR 기반 성분 정보 추출**: Clova OCR을 활용하여 제품 이미지에서 텍스트를 추출하고 정제합니다.
2. **HCX 모델 Fine-tuning**: GPT-4o를 사용해 학습 데이터를 생성하고, 이를 기반으로 HCX-003 모델을 파인튜닝합니다.
3. **HCX 모델을 통한 성분 정보 추론**: Fine-tuned HCX 모델을 사용하여 OCR 데이터를 기반으로 성분 정보를 자동 추출합니다.
4. **Rule-based vs HCX 결과 비교**: Rule-based 방식의 결과와 HCX 추론 결과의 일치도를 평가합니다.
5. **자동화된 성분 분석 파이프라인**: Object Detection → OCR → HCX 추론 → 비교 분석까지 전 과정이 자동화된 데이터 처리 워크플로우를 구축합니다.


## 폴더 구조
```bash
.
├── README.md
├── main.py                                   # 파이프라인 실행 코드
├── environment.yml                           # Conda 환경 설정 파일
├── config
│   └── config.yaml                           # YOLO 학습 및 추론 관련 설정 파일
├── data
│   ├── HCX                                   # HyperClovaX 관련 학습, 추론, 평가 데이터셋
│   │   ├── eval
│   │   ├── inference
│   │   └── train
│   ├── OCR                                   # CLOVA OCR 관련 추론 데이터셋
│   │   └── inference
│   ├── preprocessed                          # 전처리된 데이터셋 저장 폴더
│   ├── Rule-based                            # 규칙 기반 방식의 추론 및 평가 데이터셋
│   │   ├── eval
│   │   └── inference
│   └── YOLO                                  # YOLO 관련 학습, 추론, 결과 데이터셋
│       ├── inference
│       ├── output
│       └── train
├── prompt
│   ├── system_prompt_vf.txt                  # 시스템 프롬프트
│   └── user_prompt_vf.txt                    # 사용자 프롬프트
├── src
│   ├── HCX
│   │   ├── 01_HCX_dataset.py                 # HCX 데이터셋 로딩 및 처리
│   │   ├── 02_HCX_train.py                   # HCX 모델 학습 코드
│   │   ├── 03_HCX_inference.py               # HCX 모델 추론 코드
│   │   ├── 04_post_processing.py             # HCX 추론 후처리 코드
│   │   └── 05_eval_ingredient.py             # 성분 정보 평가 코드
│   ├── OCR
│   │   ├── 01_OCR_text.py                    # OCR 텍스트 추출 코드
│   │   ├── 02_OCR_row_col_323.py             # OCR 표 형식 추출 코드 (전체 데이터셋)
│   │   └── 03_OCR_row_col_273_50.py          # OCR 표 형식 추출 코드 (학습 및 평가 데이터셋)
│   ├── preprocessing
│   │   ├── 01_data_selection_323.py          # 영양/성분 정보 이미지 선택 코드 (전체 데이터셋)
│   │   └── 02_data_selection_273.py          # 영양/성분 정보 이미지 선택 코드 (학습 데이터셋)
│   ├── Rule-based
│   │   ├── 01_rule_based.py                  # 규칙 기반 방식으로 정보 추출
│   │   └── 02_eval_nutrition.py              # 영양 정보 평가 코드
│   └── YOLO
│   │   ├── 01_data_conversion.py             # 데이터 변환 코드
│   │   └── 02_YOLO.py                        # YOLO 모델 학습 및 추론 코드
└── utils
    └── utils.py                              # ingredient 관련 학습 및 평가 데이터셋 처리 코드
```


## 설치 및 실행 방법
### 1) 환경 구축
- Python 3.10.15 버전 권장
- 의존성 패키지 설치
```bash
conda env create -f environment.yml
```


### 2) 실행
- 기본 실행
```bash
python main.py
```


## Input & Output
### 1. Input:
- `data/OCR/inference/images_323_OCR_row_col.csv`, `data/OCR/inference/images_50_OCR_row_col.csv`: OCR 결과 데이터
- `data/HCX/train/finetuning_273_gpt_human_v2.csv`, `data/preprocessed/images_50.csv`: Fine-tuning 학습 데이터
- `data/HCX/eval/images_50_ingredient_processed.csv`, `data/HCX/inference/images_323_ingredient.csv`: 성분 정제 및 비교 데이터
- `prompt/*`: 시스템 및 사용자 프롬프트 템플릿
- Clova Studio API 키 및 Task ID

### 2. Output
- `data/HCX/train/HCX_train_v2.csv`: GPT-4o로 생성한 파인튜닝용 데이터
- `data/HCX/eval/finetuning_50_gpt.csv`: 평가 데이터
- `data/HCX/inference/HCX_inference_v2.csv`: Fine-tuned 모델 인퍼런스 결과
- `data/HCX/inference/images_323_ingredient.csv`: HCX 추론 결과 성분 정보




## 코드 설명
- `main.py`
    - config/config.yaml 설정 파일을 읽고, 선택한 파이프라인의 Python 스크립트를 순서대로 실행하는 스크립트 실행 관리 도구
- `src/HCX/01_HCX_dataset.py`
    - OCR 결과(ocr_data)를 user_prompt_vf.txt 템플릿에 삽입하여 프롬프트를 생성하고, 정제된 GPT 모델의 응답(reference)과 함께 새로운 학습 데이터(HCX_train_v2.csv)를 구성하는 스크립트
    - 생성된 데이터는 C_ID, T_ID, Text(프롬프트), Completion(모델 응답) 형식으로 저장
- `src/HCX/02_HCX_train.py`
    - Clova Studio API를 사용하여 HCX-003 모델의 학습(Task)을 생성하는 스크립트로, 주어진 API 키와 요청 ID를 사용해 HCX_train_v2.csv 데이터를 학습 요청으로 전송
    - 요청이 성공하면 status 코드 20000을 확인하고 결과를 반환
- `src/HCX/03_HCX_inference.py`
    - OCR 결과(images_323_OCR_row_col.csv)를 활용하여 Clova Studio의 Fine-tuned 모델을 사용해 성분 정보를 추출하고, 결과를 HCX_inference_v2.csv에 저장하는 스크립트
    - 요청 실패 시 최대 20회 재시도하며, system_prompt_vf.txt 및 user_prompt_vf.txt 프롬프트 파일을 기반으로 API 요청을 생성
- `src/HCX/04_post_processing.py`
    - HCX 모델의 추론 결과(HCX_inference_v2.csv)에서 JSON 형식의 성분 정보를 정제 및 파싱하여 개별 컬럼(원재료, 알레르기, 보관방법 등)으로 변환하고, images_323_ingredient.csv로 저장하는 스크립트
    - img-ID에서 숫자를 추출하여 정렬한 후 불필요한 컬럼을 제거하고 최종 결과를 저장
- `src/HCX/05_eval_ingredient.py`
    - OCR 기반으로 추출된 성분 정보(images_50_ingredient_processed.csv)와 HCX 모델 추론 결과(images_323_ingredient.csv)를 img-ID 기준으로 비교하여 Levenshtein 거리 및 유사도를 계산하는 스크립트
    - 각 성분 항목(원재료, 알레르기, 보관방법 등)의 평균 유사도를 출력하여 두 데이터의 일치도를 평가
- `src/OCR/01_OCR_text.py`
    - 이 코드는 YOLO 탐지된 객체의 바운딩 박스를 기준으로 이미지를 크롭한 후, Clova OCR API를 사용하여 텍스트를 추출하고 결과를 CSV 파일로 저장하는 스크립트
    - 크롭한 이미지들은 임시 폴더(temp_crop)에서 처리 후 삭제되며, OCR 결과는 | 로 구분하여 저장
- `src/OCR/02_OCR_row_col_323.py`
    - YOLO 탐지된 객체 영역을 크롭한 후, Clova OCR을 사용하여 테이블과 일반 텍스트를 추출 및 정리하여 JSON 형식으로 저장한 후, CSV 파일로 저장하는 스크립트
    - OCR 결과는 행(row), 열(col) 정보를 포함한 키로 그룹화하여 정리
- `src/OCR/03_OCR_row_col_273_50.py`
    - 이미지 ID(img-ID)를 기준으로 images_323_OCR_row_col.csv에서 images_273.csv와 images_50.csv에 포함된 데이터만 필터링하여 각각 새로운 CSV 파일(images_273_OCR_row_col.csv, images_50_OCR_row_col.csv)로 저장하는 스크립트
- `src/Rule-based/01_rule_based.py`
    - OCR 결과에서 영양성분 정보를 정규식을 활용해 추출한 후, images_323_nutrition.csv로 저장하는 스크립트
    - img-ID에서 숫자를 추출하여 정렬한 후, 필요 없는 컬럼을 제거하고 최종 결과를 저장
- `src/Rule-based/02_eval_nutrition.py`
    - OCR에서 추출한 영양정보(images_323_nutrition.csv)와 정답 데이터(total_nutrition.csv)를 ID를 기준으로 비교하여 각 영양성분별 일치 여부를 분석하고, 전체 및 개별 항목의 일치 확률을 계산하는 스크립트
- `src/YOLO/01_data_conversion.py`
    - CSV 파일에서 이미지 URL과 ID를 읽어와, 이미지를 다운로드하여 지정된 폴더(YOLO/inference/images, YOLO/train/images)에 저장하는 스크립트
    - 이미지 파일명은 img-ID 값을 기반으로 특수문자를 제거한 후 .png 확장자로 저장
- `src/YOLO/02_YOLO.py`
    - 이 코드는 YOLO 모델(yolo11n.pt)을 로드하여 학습하고, 지정된 폴더의 이미지에 대해 객체 탐지를 수행한 후 결과 이미지를 저장하는 스크립트
    - 탐지된 객체 정보를 YOLO 형식의 라벨(txt) 파일로 저장
- `utils/utils.py`
    - OCR 데이터와 학습 데이터(finetuning_273_gpt_human_v2.csv)를 병합 및 후처리하여 정제된 데이터셋을 생성하고, OpenAI GPT 모델을 활용해 OCR 결과를 평가한 후, 최종적으로 정리된 영양 성분 및 원재료 정보를 포함한 평가 데이터셋을 생성하는 스크립트
    - 실행 단계는 OCR 병합 → 학습 데이터 후처리 → 평가 데이터 생성 → 평가 데이터 후처리 순서로 진행