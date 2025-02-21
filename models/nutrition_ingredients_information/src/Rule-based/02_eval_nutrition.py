import pandas as pd
import re

# 영양 정보 추출 함수
def extract_nutrition_info(text):
    if pd.notnull(text):
        patterns = {
            "sodium": r'나트륨.*?g',
            "carb": r'탄수화물.*?g',
            "sugar": r'당류.*?g',
            "fat": r'지방.*?g',
            "trans_fat": r'트랜스지방.*?g',
            "saturated_fat": r'포화지방.*?g',
            "cholesterol": r'콜레스테롤.*?g',
            "protein": r'단백질.*?g'
        }
        
        extracted_values = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                extracted_values[key] = re.sub(r'\s+', '', match.group(0))  # 공백 제거
            else:
                extracted_values[key] = None
        
        return extracted_values
    
    return {key: None for key in patterns.keys()}

# CSV 파일 불러오기
images_df = pd.read_csv("data/Rule-based/inference/images_323_nutrition.csv")
total_df = pd.read_csv("data/Rule-based/eval/total_nutrition.csv")

# img-ID에서 마지막 두 글자 제거하여 ID 컬럼 추가
images_df["ID"] = images_df["img-ID"].astype(str).str[:-2]

# ID를 기준으로 두 데이터프레임을 병합
merged_df = pd.merge(images_df, total_df, on="ID", how="inner")

# 영양 정보 추출 (각 개별 값 비교)
merged_df["Extracted_Nutrition_images"] = merged_df["영양정보_x"].apply(extract_nutrition_info)
merged_df["Extracted_Nutrition_total"] = merged_df["영양정보_y"].apply(extract_nutrition_info)

# 각 영양소별 비교하여 일치하면 1, 다르면 0
nutrition_keys = ["sodium", "carb", "sugar", "fat", "trans_fat", "saturated_fat", "cholesterol", "protein"]

for key in nutrition_keys:
    merged_df[f"Match_{key}"] = merged_df.apply(
        lambda row: 1 if row["Extracted_Nutrition_images"][key] == row["Extracted_Nutrition_total"][key] else 0,
        axis=1
    )

# 총합 계산
merged_df["Total_Match"] = merged_df[[f"Match_{key}" for key in nutrition_keys]].sum(axis=1)

# 전체 데이터 개수
total_count = len(merged_df)

# 총 일치 개수
total_match_count = merged_df['Total_Match'].sum()

# 각 항목별 일치 개수 및 확률 계산
match_summary = merged_df[[f"Match_{key}" for key in nutrition_keys]].sum()
match_percentage = (match_summary / total_count) * 100

total_match_percentage = (total_match_count / (total_count * len(nutrition_keys))) * 100

# 결과 출력
print(f"전체 {total_count * len(nutrition_keys)}개 중 {total_match_count}개 일치")
print(f"총 일치 확률: {total_match_percentage:.2f}%")
print("각 항목별 일치 개수 및 확률:")
print(pd.DataFrame({"일치 개수": match_summary, "일치 확률(%)": match_percentage}))
