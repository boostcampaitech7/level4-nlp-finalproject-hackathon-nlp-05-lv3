import argparse
import csv
import os
import requests
import json
from io import BytesIO
from PIL import Image
import yaml
import logging
import openai  # pip install openai

def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def clean_response_text(text: str) -> str:
    """
    응답 텍스트에서 Markdown 코드 블록(백틱)을 제거합니다.
    """
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[-1].strip().startswith("```"):
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        text = "\n".join(lines).strip()
    return text

def analyze_image_with_gpt4o(img_url: str, client: object) -> dict:
    """
    GPT-4o를 활용하여 제품 이미지를 분석하고,
    texture, shape, color, transparency, design 정보를 추출합니다.
    
    반환 JSON 형식:
    {
        "texture": "예: plastic",
        "shape": "예: rectangular",
        "color": "예: primary: red, secondary: black",
        "transparency": "Yes or No",
        "design": "전체 디자인에 대한 한줄 설명"
    }
    """
    prompt = (
        "Analyze the following product image and extract the details in English. "
        "Provide the answer strictly in JSON format with the following keys:\n\n"
        "1. texture\n2. shape\n3. color\n4. transparency\n5. design\n\n"
        "Return your answer only as a JSON object."
    )
    
    try:
        response = client.ChatCompletion.create(
            model="gpt-4o",  
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": img_url}},
                    ],
                }
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        # 응답 메시지의 텍스트 내용 접근
        response_text = response.choices[0].message.content
        logging.info("DEBUG: Raw response text: %s", response_text)
        cleaned_text = clean_response_text(response_text)
        logging.info("DEBUG: Cleaned response text: %s", cleaned_text)
        if not cleaned_text.strip():
            raise ValueError("Received empty response text from the API.")
        result = json.loads(cleaned_text)
    except Exception as e:
        logging.error("Error during GPT-4o analysis: %s", e)
        result = {"texture": "", "shape": "", "color": "", "transparency": "", "design": ""}
    return result

def process_csv(input_csv: str, output_csv: str, client: object, start_row: int = 324):
    """
    input_csv 파일의 각 행에 대해 "대표 이미지 URL"에서 이미지를 접근 가능한지 확인하고,
    GPT-4o를 사용하여 제품 정보를 추출한 후, output_csv 파일에 저장합니다.
    
    출력 CSV는 다음 열을 반드시 포함합니다:
    "대표 이미지 URL", "texture", "shape", "color", "transparency", "design"
    """
    # 출력 CSV가 이미 존재하면 append, 없으면 새로 작성
    if os.path.exists(output_csv):
        output_mode = 'a'
        write_header = False
    else:
        output_mode = 'w'
        write_header = True

    with open(input_csv, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        with open(output_csv, output_mode, newline='', encoding='utf-8') as outfile:
            fieldnames = ["대표 이미지 URL", "texture", "shape", "color", "transparency", "design"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            for i, row in enumerate(reader, start=0):
                # start_row 이전의 행은 건너뛰기
                if i < start_row:
                    continue

                image_url = row.get("대표 이미지 URL", "").strip()
                if not image_url:
                    logging.info("Row %s: Empty image_url; skipping row.", i)
                    continue

                # 이미지 URL의 접근성 확인
                try:
                    resp = requests.get(image_url, timeout=10)
                    resp.raise_for_status()
                except Exception as e:
                    logging.error("Row %s: Failed to access image from %s: %s", i, image_url, e)
                    continue

                # GPT-4o를 이용한 이미지 분석 수행
                analysis = analyze_image_with_gpt4o(image_url, client)

                output_row = {
                    "대표 이미지 URL": image_url,
                    "texture": analysis.get("texture", ""),
                    "shape": analysis.get("shape", ""),
                    "color": analysis.get("color", ""),
                    "transparency": analysis.get("transparency", ""),
                    "design": analysis.get("design", "")
                }
                writer.writerow(output_row)
                logging.info("Row %s: Processed: %s", i, image_url)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    parser = argparse.ArgumentParser(description="GPT-4o 이미지 분석 및 CSV 처리")
    parser.add_argument(
        "--config",
        "-c",
        default="config/config.yaml",
        help="설정 파일 경로 (기본값: config/config.yaml)"
    )
    args = parser.parse_args()

    # 설정 파일 로드
    config = load_config(args.config)

    # OpenAI API 키 설정 (config.yaml의 openai 섹션 활용)
    openai_api_key = config.get("openai", {}).get("api_key", "")
    if not openai_api_key:
        raise ValueError("OpenAI API key is not provided in config.")
    openai.api_key = openai_api_key

    # OpenAI 클라이언트 (openai 모듈 사용)
    client = openai

    # CSV 파일 경로 설정 (config.yaml의 paths 섹션 활용)
    data_dir = config.get("paths", {}).get("data_dir", "./data")
    input_csv_filename = config.get("paths", {}).get("thumbnail_1347", "thumbnail_1347.csv")
    output_csv_filename = config.get("paths", {}).get("thumbnail_1347_gpt_train", "thumbnail_1347_gpt_train")
    input_csv = os.path.join(data_dir, input_csv_filename)
    output_csv = os.path.join(data_dir, output_csv_filename)

    logging.info("Input CSV: %s", input_csv)
    logging.info("Output CSV: %s", output_csv)

    process_csv(input_csv, output_csv, client)

if __name__ == "__main__":
    main()