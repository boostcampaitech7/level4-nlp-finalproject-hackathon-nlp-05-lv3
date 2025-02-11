import pandas as pd
import ast
import json
import re

# CSV 파일 로드
file_path = "data/HCX/inference/HCX_inference_v2.csv"
df = pd.read_csv(file_path)

# 성분정보 컬럼 JSON 변환 함수
def clean_json_format(value):
    try:
        # 튜플 형식이면 첫 번째 요소만 추출
        if isinstance(value, str) and value.startswith("('{"):
            value = ast.literal_eval(value)[0]  # 튜플의 첫 번째 요소 가져오기
        
        # JSON 문자열을 올바르게 변환
        cleaned_json = json.loads(value)
        return json.dumps(cleaned_json, ensure_ascii=False)
    except Exception as e:
        return value  # 변환 실패 시 원본 값 유지

# 변환 적용
df["성분정보"] = df["성분정보"].apply(clean_json_format)

# JSON 데이터를 파싱하여 개별 컬럼으로 변환하는 함수
def parse_json(json_str):
    try:
        # 문자열 확인 후 JSON 변환 시도
        if isinstance(json_str, str):
            data = json.loads(json_str.replace("'", "\""))  # 작은따옴표 변환 후 JSON 로드
        else:
            return pd.Series(["오류", "오류", "오류", "오류", "오류"])

        # 원재료 및 알레르기 정보 추출
        원재료 = ", ".join(data.get("원재료", [])) if isinstance(data.get("원재료"), list) else ""
        알레르기_1차 = ", ".join(data.get("알레르기(1차)", [])) if isinstance(data.get("알레르기(1차)"), list) else ""
        알레르기_2차 = ", ".join(data.get("알레르기(2차)", [])) if isinstance(data.get("알레르기(2차)"), list) else ""

        # 보관방법을 문자열 그대로 가져오고, 필요한 값만 추출
        보관방법_raw = str(data.get("보관방법", "{}"))  # dict -> str 변환

        # 안전하게 딕셔너리로 변환 시도
        try:
            보관방법_dict = ast.literal_eval(보관방법_raw) if "{" in 보관방법_raw else {}
        except (ValueError, SyntaxError):
            보관방법_dict = {}

        보관방법_개봉전 = 보관방법_dict.get("개봉전", "") if isinstance(보관방법_dict, dict) else ""
        보관방법_개봉후 = 보관방법_dict.get("개봉후", "") if isinstance(보관방법_dict, dict) else ""

        return pd.Series([원재료, 알레르기_1차, 알레르기_2차, 보관방법_개봉전, 보관방법_개봉후])
    
    except (json.JSONDecodeError, TypeError):
        # JSON 파싱 실패 시 오류 반환
        return pd.Series(["오류", "오류", "오류", "오류", "오류"])

# 'reference' 컬럼의 JSON 데이터를 개별 컬럼으로 변환
df[["원재료", "알레르기(1차)", "알레르기(2차)", "보관방법(개봉전)", "보관방법(개봉후)"]] = df["성분정보"].apply(parse_json)

# -------------------------
def extract_number_from_img_id(img_id):
    match = re.search(r'-(\d+)-', img_id)
    return int(match.group(1)) if match else float('inf')

df['정렬번호'] = df['img-ID'].apply(lambda x: extract_number_from_img_id(str(x)))
df.sort_values(by='정렬번호', ascending=True, inplace=True)
# -------------------------

# 필요한 컬럼만 남기기
df = df[["img-ID", "원재료", "알레르기(1차)", "알레르기(2차)", "보관방법(개봉전)", "보관방법(개봉후)"]]

# 변환된 데이터 저장
df.to_csv("data/HCX/inference/images_323_ingredient.csv", index=False, encoding="utf-8-sig")
