import pandas as pd

# 파일 경로 설정
images_323_file = "data/preprocessed/images_323.csv"
images_50_file = "data/preprocessed/images_50.csv"
output_file = "data/preprocessed/images_273.csv"

# CSV 파일 읽기
df_390 = pd.read_csv(images_323_file)
df_50 = pd.read_csv(images_50_file)

# images_50.csv에 있는 img-ID 목록 가져오기
exclude_img_ids = set(df_50['img-ID'])

# images_390.csv에서 img-ID가 제외 리스트에 없는 데이터만 필터링
filtered_df = df_390[~df_390['img-ID'].isin(exclude_img_ids)]

# 필터링된 데이터를 새로운 CSV로 저장
filtered_df.to_csv(output_file, index=False)
