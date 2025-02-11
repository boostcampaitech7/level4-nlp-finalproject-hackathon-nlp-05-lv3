import os
import csv
import json
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
import re

def clova_ocr(image_path, secret_key):
    
    url = "https://zpojzpbnkf.apigw.ntruss.com/custom/v1/37528/65e67b30b3cc8f4d84245194c2415f0c980675f1f0961dbfc2ecc51a368e238c/general"
    
    headers = {'X-OCR-SECRET': secret_key}
    payload = {
        'message': json.dumps({
            "version": "v2",
            "requestId": "1234",
            "timestamp": 1722225600000,
            "lang": "ko",
            "enableTableDetection": "True",
            "images": [{"format": "jpg", "name": os.path.basename(image_path)}]
        })
    }

    with open(image_path, 'rb') as img_file:
        files = {'file': (os.path.basename(image_path), img_file, 'image/jpeg')}
        response = requests.post(url, headers=headers, data=payload, files=files)
    
        if response.status_code == 200:
            return response.json()
        else:
            print(f"OCR 요청 실패! Status Code: {response.status_code}")
            return None

def extract_grouped_text(ocr_data):
    grouped_text = {}

    # -------------------------
    # 1) 테이블 데이터 처리
    # -------------------------
    max_row_index = -1  # 테이블 중 가장 큰 rowIndex 확인용
    for image in ocr_data.get("images", []):
        for table in image.get("tables", []):
            for cell in table.get("cells", []):
                row = cell.get("rowIndex", 0)
                col = cell.get("columnIndex", 0)
                max_row_index = max(max_row_index, row)

                # 이 셀의 모든 단어를 합침
                cell_text = []
                for line in cell.get("cellTextLines", []):
                    for word in line.get("cellWords", []):
                        text = word.get("inferText", "")
                        if text:
                            cell_text.append(text)

                # "Row:x, Col:y" 형태로 묶어서 저장
                key = f"({row},{col})"
                if key not in grouped_text:
                    grouped_text[key] = []
                grouped_text[key].extend(cell_text)

    # -------------------------
    # 2) fields 데이터 처리
    # -------------------------
    # 테이블이 하나도 없었다면 max_row_index = -1, fields는 Row=0부터 시작
    field_row_index = max_row_index + 1 if max_row_index != -1 else 0

    for image in ocr_data.get("images", []):
        for field in image.get("fields", []):
            infer_text = field.get("inferText", "")
            if not infer_text:
                continue
            
            # fields는 (field_row_index, 0)에 저장
            key = f"({field_row_index},0)"
            if key not in grouped_text:
                grouped_text[key] = []
            grouped_text[key].append(infer_text)
            
            field_row_index += 1  # 다음 필드 행은 +1

    # -------------------------
    # 3) row-col 순으로 정렬하여 반환
    # -------------------------
    def parse_key(k: str):
        k = k.strip("()")
        return tuple(map(int, k.split(',')))

    sorted_keys = sorted(grouped_text.keys(), key=parse_key)
    grouped_text_sorted = {k: grouped_text[k] for k in sorted_keys}
    return grouped_text_sorted

def get_img_id(filename):
    if filename == "emart35110.png":
        return "emart-351-10"
    
    match = re.search(r'(emart)(\d+)(\d)(?=\.)', filename)
    
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    return filename

def crop_and_ocr(image_dir, label_dir, output_csv_path, secret_key):

    os.makedirs("temp_crop", exist_ok=True)  # 임시 폴더 생성
    image_extensions = ('.png', '.jpg', '.jpeg')
    
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(image_extensions)]
    df = pd.DataFrame({'img-ID': [get_img_id(f) for f in image_files], 'OCR 결과': ""})
    
    for index, row in df.iterrows():
        image_filename = image_files[index]
        image_path = os.path.join(image_dir, image_filename)
        label_path = os.path.join(label_dir, image_filename.rsplit(".", 1)[0] + ".txt")
        
        if not os.path.exists(label_path):
            print(f"라벨 파일 없음: {label_path}")
            df.at[index, 'OCR 결과'] = "라벨 파일 없음"
            continue
        
        # 이미지 로드
        image = Image.open(image_path)
        img_width, img_height = image.size
        
        # YOLO 결과 읽기
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        ocr_results = []
        
        for i, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) != 5:
                continue  # YOLO 형식이 맞지 않으면 스킵
            
            class_id, cx, cy, w, h = map(float, parts)
            
            # class_id가 1이 아닌 경우 건너뜀
            if int(class_id) != 1:
                continue
            
            # 바운딩 박스 좌표 변환 (YOLO 정규화된 값 → 실제 픽셀 좌표)
            x1 = int((cx - w / 2) * img_width)
            y1 = int((cy - h / 2) * img_height)
            x2 = int((cx + w / 2) * img_width)
            y2 = int((cy + h / 2) * img_height)

            # 좌표 검증
            if x1 < 0 or y1 < 0 or x2 > img_width or y2 > img_height or x2 <= x1 or y2 <= y1:
                print(f"잘못된 좌표 스킵: {x1}, {y1}, {x2}, {y2}")
                continue
            
            # 이미지 크롭
            cropped_img = image.crop((x1, y1, x2, y2))
            cropped_path = f"temp_crop/crop_{index}_{i}.jpg"
            cropped_img.save(cropped_path)

            # OCR 수행
            ocr_data = clova_ocr(cropped_path, secret_key)
            grouped_result = extract_grouped_text(ocr_data) 
            for key, value in grouped_result.items():
                grouped_result[key] = " ".join(value)
        
        df.at[index, 'OCR 결과'] = json.dumps(grouped_result, ensure_ascii=False)

    df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

# OCR 실행
secret_key = 'YOUR_SECRET_KEY'
image_dir = 'data/YOLO/output/images/'
label_dir = 'data/YOLO/output/labels/'
output_csv_path = 'data/OCR/inference/images_323_OCR_row_col.csv'

crop_and_ocr(image_dir, label_dir, output_csv_path, secret_key)
