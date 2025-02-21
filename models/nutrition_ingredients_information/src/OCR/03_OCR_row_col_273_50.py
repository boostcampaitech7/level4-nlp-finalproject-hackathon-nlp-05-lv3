import pandas as pd

# CSV 파일 로드
images_323_OCR = pd.read_csv('data/OCR/inference/images_323_OCR_row_col.csv')
images_273 = pd.read_csv("data/preprocessed/images_273.csv")
images_50 = pd.read_csv("data/preprocessed/images_50.csv")

# img-ID 컬럼을 기준으로 필터링
filtered_data_273 = images_323_OCR[images_323_OCR['img-ID'].isin(images_273['img-ID'])]
filtered_data_50 = images_323_OCR[images_323_OCR['img-ID'].isin(images_50['img-ID'])]

# 결과를 새로운 CSV 파일로 저장
filtered_data_273.to_csv("data/OCR/inference/images_273_OCR_row_col.csv", index=False)
filtered_data_50.to_csv("data/OCR/inference/images_50_OCR_row_col.csv", index=False)
