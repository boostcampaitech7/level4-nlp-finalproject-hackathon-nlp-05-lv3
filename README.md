# 대표 이미지 설명

> 작성자 : 윤선웅  
> 대표 이미지 설명 기능은 시각장애인 사용자가 상품의 외형과 포장 상태를 보다 쉽게 파악할 수 있도록 돕습니다.  
> 이 기능을 통해 상품 대표 이미지에 대한 포장 상태(색상, 재질, 투명성 등), 구성, 디자인 등의 시각적 정보를 제공합니다.  
> 시각장애인 사용자가 상품의 외형과 포장 상태를 이해하여 보다 편리한 온라인 쇼핑 경험을 지원합니다.

---

## 개요

시각장애인 사용자에게 **상품 이미지**를 객관적이고 간결하게 설명하기 위한 시스템을 구성합니다.

1. **VLM 모델 Inference**  
   - Janus-Pro, Qwen2.5_VL 등을 통해 대표 이미지에 대한 설명을 생성합니다.
2. **후처리 (Post_processing)**  
   - HyperCLOVA HCX-003 모델을 활용하여 번역 및 Few-shot 방식 등을 통해 설명의 품질을 높입니다.
3. **파인튜닝 (Finetuning)**  
   - GPT-4o로 생성한 학습 데이터로 Janus-Pro를 파인튜닝하여 정교한 설명 성능에 도전합니다. (TBD)
4. **평가 (Evaluation)**  
   - OpenAI GPT-4o 모델을 활용해 점수를 매겨 설명의 품질을 측정할 수 있습니다.

> `config.yaml`에서 **API Key, 파일 경로**, 실행 여부 등을 관리하여 파이프라인을 유연하게 제어합니다.

---

## 폴더 구조

```bash
thumbnail_description/
├── config
│   └── config.yaml                # 설정 파일(API Key, 경로, 파이프라인 실행 여부)
├── data
│   ├── ... (각종 CSV 데이터)
│   └── ...
├── hcx_prompt
│   ├── system_janus_pro_hcx_fewshot.txt
│   ├── system_janus_pro_hcx_translation.txt
│   ├── system_qwen2_5_pp_hcx.txt
│   ├── user_janus_pro_hcx_fewshot.txt
│   ├── user_janus_pro_hcx_translation.txt
│   └── user_qwen2_5_pp_hcx.txt
├── prompt
│   ├── deepseek_prompt.txt
│   ├── janus_prompt.txt
│   ├── maal_prompt.txt
│   ├── qwen2_5_prompt.txt
│   ├── qwen2_prompt.txt
│   └── unsloth_prompt.txt
├── src
│   ├── description
│   │   ├── deepseekvl.py              # DeepSeek_VL을 활용한 썸네일 설명 생성
│   │   ├── janus_pro.py                # Janus Pro을 활용한 썸네일 설명 생성
│   │   ├── maal.py                     # MAAL을 활용한 썸네일 설명 생성
│   │   ├── qwen2_5_vl.py               # Qwen2.5_VL을 활용한 썸네일 설명 생성
│   │   ├── qwen2_vl.py                 # Qwen2_VL을 활용한 썸네일 설명 생성
│   │   └── unsloth_qwen2_vl.py         # Unsloth_Qwen2_VL을 활용한 썸네일 설명 생성
│   ├── post_processing                 
│   │   ├── janus_pro_hcx_translation.py  # Janus Pro 모델의 HCX 기반 번역 후처리
│   │   ├── janus_pro_papago_translation.py  # Papago 번역을 활용한 Janus Pro 후처리
│   │   ├── janus_pro_pp_hcx.py         # Janus Pro 모델의 PP-HCX 기반 후처리
│   │   └── qwen2_5_pp_hcx.py           # Qwen2.5 모델의 PP-HCX 기반 후처리
│   ├── evaluation                      
│   │   ├── gpt_eval.py                 # GPT 기반 평가셋 썸네일 설명 평가
│   │   └── gpt_eval_323.py             # GPT 기반 전체 데이터 셋 썸네일 설명 평가
├── utils
│   ├── __init__.py
│   └── common_utils.py                 # 공통 유틸리티 함수 정의
└── main.py                             # 메인 실행 파일
```
---

## 입력(Input)과 출력(Output)

### 입력

1. **상품 대표 이미지 및 메타데이터**
   - **이미지 파일**:  
     온라인 쇼핑몰에서 제공하는 상품 대표 이미지가 시스템의 주요 입력 데이터입니다.
   - **CSV 데이터**:  
     `data` 폴더 내의 CSV 파일들은 각 상품에 대한 추가 메타데이터(예: 상품 코드, 카테고리, 기존 설명 등)를 포함하며, 이미지와 연계되어 후처리 및 평가 과정에서 활용됩니다.

2. **설정 정보 및 API 인증**
   - **config.yaml**:  
     API Key, 파일 경로, 파이프라인 실행 여부 등 전체 시스템의 설정 정보를 포함합니다.
   - **번역 및 후처리 관련 설정**:  
     HyperCLOVA HCX-003, OpenAI API Key 등 후처리와 평가에 필요한 인증 정보와 파라미터를 포함합니다.

3. **프롬프트 텍스트**
   - **hcx_prompt 폴더**:  
     Janus-Pro, Qwen2.5_VL 등 다양한 모델의 번역 및 Few-shot 학습에 필요한 프롬프트 텍스트를 저장합니다.
   - **prompt 폴더**:  
     DeepSeek, Janus, MAAL, Qwen2_VL 등 다양한 VLM 모델에 대한 인퍼런스 요청 프롬프트를 포함합니다.

---

### 출력 (Output)

1. **썸네일 이미지에 대한 텍스트 설명**
   - **기본 생성 결과**:  
     `src/description` 폴더 내의 각 모듈(예: `janus_pro.py`, `qwen2_5_vl.py` 등)은 입력된 상품 이미지를 기반으로 포장 상태(색상, 재질, 투명성), 구성, 디자인 등의 시각적 정보를 포함한 텍스트 설명을 생성합니다.
   - **후처리된 결과**:  
     - `src/post_processing` 폴더 내의 스크립트들은 초기 생성된 텍스트 설명을 번역(Papago 또는 HCX 기반)하거나 Few-shot 기법을 활용해 품질을 보정합니다.
     - 예를 들어, `janus_pro_hcx_translation.py`와 `qwen2_5_pp_hcx.py` 모듈은 각각 해당 모델의 출력에 대해 후처리를 수행합니다.

2. **평가 및 점수 정보**
   - **GPT 평가 결과**:  
     `src/evaluation` 폴더의 `gpt_eval.py` 및 `gpt_eval_323.py` 스크립트는 GPT-4o 모델 등을 활용하여 생성된 텍스트 설명의 품질을 평가합니다.
   - **전체 파이프라인 평가**:  
     평가 결과는 최종 출력물의 신뢰도와 품질 개선에 활용되며, 파인튜닝(예: Janus-Pro Finetuning) 등에 반영됩니다.

3. **최종 사용자 제공 결과**
   - **시각장애인 대상 설명 텍스트**:  
     최종 출력은 시각장애인 사용자가 상품의 외형과 포장 상태를 보다 쉽게 이해할 수 있도록 간결하고 객관적인 텍스트 설명 형태로 제공됩니다.
   - **저장 및 활용**:  
     최종 결과는 설정된 파일 경로에 저장되며, 이후 사용자 인터페이스(예: 온라인 쇼핑몰)에 통합되어 실제 서비스에 활용됩니다.

---
## 설치 및 실행 방법
### 1) 환경 구축
- Python 3.10.15 버전 권장
- 의존성 패키지 설치
```bash
conda env create -f environment.yml
```

### 2) 설정
- `config/config.yaml` 파일에서 다음 정보를 적절히 설정합니다.
    - **API Key / Request ID**: HyperCLOVA X 인증 정보
    - **OpenAI API Key**: GPT 모델 사용 시 필요
    - **파일 경로**: 데이터 파일 위치, 파인튜닝 결과 저장 경로 등
    - **파이프라인 실행 여부**: `true`/`false` 값으로 모델추론/후처리/평가 등 단계별 실행 제어
    - **파인튜닝 설정**: TBD

### 3) 실행
- 기본 실행 (기본 `config/config.yaml` 사용 시)
```bash
python main.py
```
- 별도 설정파일 사용
```bash
python main.py --config config/config_name.yaml
```
---
