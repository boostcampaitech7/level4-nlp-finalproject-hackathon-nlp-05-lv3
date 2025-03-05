import pandas as pd

# 원본 CSV 파일 경로
input_file = "data/preprocessed/eda_final_emartmall_full.csv"
output_file = "data/preprocessed/images_323.csv"

# CSV 파일 읽기
df = pd.read_csv(input_file, encoding='cp949')

# 필터링: 이미지 URL이 특정 문자열로 끝나고, "순서 유지" 값이 'O'인 경우
filtered_df = df[
    df['이미지 URL'].str.endswith("jpg?ref=storefarm", na=False) & (df['순서 유지'] == 'O')
]

# 필요한 컬럼만 선택
filtered_df = filtered_df[['img-ID', '이미지 URL']]

# 필터링된 데이터를 새로운 CSV로 저장
filtered_df.to_csv(output_file, index=False)
