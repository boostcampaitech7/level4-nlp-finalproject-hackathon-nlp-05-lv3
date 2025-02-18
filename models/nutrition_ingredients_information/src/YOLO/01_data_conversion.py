import pandas as pd
import os
import re
import requests

# CSV 파일 읽기
def load_csv(file_path):
    return pd.read_csv(file_path, dtype=str)

# 저장 폴더 생성
def create_folder(folder_path):
    os.makedirs(folder_path, exist_ok=True)

# 파일명 정리 함수
def clean_filename(filename):
    return re.sub(r"[^\w가-힣]", "", filename)

# 이미지 다운로드 및 저장
def download_images(data, download_folder):
    create_folder(download_folder)
    
    for index, row in data.iterrows():
        image_url = row["이미지 URL"]
        product_name = clean_filename(row["img-ID"]) + ".png"
        save_path = os.path.join(download_folder, product_name)
        
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(save_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Saved: {save_path}")
            else:
                print(f"Failed to download {image_url}")
        except Exception as e:
            print(f"Error downloading {image_url}: {e}")

# 파일 경로 설정
file_paths = {
    "data/preprocessed/images_323.csv": "data/YOLO/inference/images",
    "data/preprocessed/images_273.csv": "data/YOLO/train/images"
}

# 이미지 다운로드 실행
for file_path, folder in file_paths.items():
    data = load_csv(file_path)
    download_images(data, folder)
