import pandas as pd

# 파일 경로 설정
prompt_file = "prompt/user_prompt_vf.txt"
completion_file = "data/HCX/train/HCX_273_gpt_processed_v2.csv"
output_file = "data/HCX/train/HCX_train_v2.csv"

# 텍스트 파일에서 전체 프롬프트 로드
with open(prompt_file, "r", encoding="utf-8") as f:
    prompt_template = f.read().strip()

# CSV 파일에서 Completion 및 OCR 결과 데이터 로드
completion_df = pd.read_csv(completion_file, encoding="utf-8")

# reference 및 ocr_data 컬럼 데이터 추출 (NaN 값 제거)
completions = completion_df["reference"].dropna().tolist()
ocr_results = completion_df["ocr_data"].dropna().tolist()

# 데이터 크기를 맞추기 위해 세 리스트 중 최소 길이에 맞춤
min_length = min(len(completions), len(ocr_results))

# 프롬프트 내 {ocr_data}를 각 ocr_data 값으로 치환하여 리스트 생성
processed_prompts = [
    prompt_template.replace("{ocr_data}", str(ocr_results[i])) for i in range(min_length)
]

# 데이터프레임 생성
df = pd.DataFrame({
    "C_ID": list(range(min_length)),
    "T_ID": [0] * min_length,
    "Text": processed_prompts,
    "Completion": completions[:min_length]
})

# CSV 파일로 저장
df.to_csv(output_file, index=False, encoding="utf-8")
