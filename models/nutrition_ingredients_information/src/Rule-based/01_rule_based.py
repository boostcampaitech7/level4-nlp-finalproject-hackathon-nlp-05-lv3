import re
import pandas as pd

csv_file_path = 'data/OCR/inference/images_323_OCR_text.csv'
df = pd.read_csv(csv_file_path)

def extract_nutrition_info(text):
    if pd.notnull(text):
        pattern_g = r'\d+\.?\d*\s*g(?=.*나트륨)'
        pattern_ml = r'\d+\.?\d*\s*ml(?=.*나트륨)'
        pattern_mL = r'\d+\.?\d*\s*mL(?=.*나트륨)'
        pattern_kcal = r'\d+\.?\d*\s*kcal(?=.*나트륨)'
        pattern_sodium = r'나트륨.*?g'
        pattern_carb = r'탄수화물.*?g'
        pattern_sugar = r'당류.*?g'
        pattern_fat = r'지방.*?g'
        pattern_trans_fat = r'트랜스지방.*?g'
        pattern_saturated_fat = r'포화지방.*?g'
        pattern_cholesterol = r'콜레스테롤.*?g'
        pattern_protein = r'단백질.*?g'
        
        match_g = re.search(pattern_g, text)
        match_ml = re.search(pattern_ml, text)
        match_mL = re.search(pattern_mL, text)
        match_kcal = re.search(pattern_kcal, text)
        match_sodium = re.search(pattern_sodium, text)
        match_carb = re.search(pattern_carb, text)
        match_sugar = re.search(pattern_sugar, text)
        match_fat = re.search(pattern_fat, text)
        match_trans_fat = re.search(pattern_trans_fat, text)
        match_saturated_fat = re.search(pattern_saturated_fat, text)
        match_cholesterol = re.search(pattern_cholesterol, text)
        match_protein = re.search(pattern_protein, text)
        
        nutrition_info = [
            match_g.group(0) if match_g else '',
            match_ml.group(0) if match_ml else '',
            match_mL.group(0) if match_mL else '',
            match_kcal.group(0) if match_kcal else '',
            match_sodium.group(0) if match_sodium else '',
            match_carb.group(0) if match_carb else '',
            match_sugar.group(0) if match_sugar else '',
            match_fat.group(0) if match_fat else '',
            match_trans_fat.group(0) if match_trans_fat else '',
            match_saturated_fat.group(0) if match_saturated_fat else '',
            match_cholesterol.group(0) if match_cholesterol else '',
            match_protein.group(0) if match_protein else ''
        ]
        
        return ', '.join(filter(None, nutrition_info)) if any(nutrition_info) else None
    
    return None

df['영양정보'] = df['OCR 결과'].apply(lambda x: extract_nutrition_info(x))

# -------------------------
def extract_number_from_img_id(img_id):
    match = re.search(r'-(\d+)-', img_id)
    return int(match.group(1)) if match else float('inf')

df['정렬번호'] = df['img-ID'].apply(lambda x: extract_number_from_img_id(str(x)))
df.sort_values(by='정렬번호', ascending=True, inplace=True)
df.drop(columns=['정렬번호', 'OCR 결과'], inplace=True)
# -------------------------

output_csv_path = 'data/Rule-based/inference/images_323_nutrition.csv'
df.to_csv(output_csv_path, index=False)
