import os
import time
import yaml
import pandas as pd
import torch

from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

from utils.common_utils import set_seed, load_and_filter_data

def run_inference_qwen2_vl():
    """
    Qwen2-VL-7B-Instruct 모델을 활용하여 CSV 데이터 내 이미지에 대해
    추론을 수행한 뒤 결과를 CSV 파일에 저장.
    config.yaml에서 경로를 불러옵니다.
    """
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    data_dir   = config["paths"]["data_dir"]          
    prompt_dir = config["paths"]["prompt_dir"]        
    csv_name   = config["paths"]["cleaned_text_contents"]  
    out_name   = config["paths"]["qwen2_eval"]        

    # 실제 경로 구성
    csv_path    = os.path.join(data_dir, csv_name)           
    prompt_path = os.path.join(prompt_dir, "qwen2_prompt.txt") 
    output_csv  = os.path.join(data_dir, out_name)           

    # 시드 설정
    set_seed(42)

    # CSV 로드 & 필터링
    df_filtered = load_and_filter_data(csv_path)
    image_urls  = df_filtered['url_clean'].to_list()
    product_names = df_filtered['상품명'].to_list()

    # 프롬프트 읽기
    with open(prompt_path, "r", encoding="utf-8") as f:
        base_prompt = f.read().strip()

    print("[Qwen2-VL] Loading model and processor...")
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2-VL-7B-Instruct", torch_dtype="auto", device_map="auto"
    )
    # 이미지 토큰화 파라미터
    min_pixels = 256 * 28 * 28
    max_pixels = 1280 * 28 * 28
    processor = AutoProcessor.from_pretrained(
        "Qwen/Qwen2-VL-7B-Instruct", min_pixels=min_pixels, max_pixels=max_pixels
    )

    model_name = "qwen2-vl"
    results = []

    def process_qwen2_vl(img_url, prompt_text):
        """
        단일 이미지 URL과 프롬프트로 Qwen2-VL 모델을 추론하는 내부 함수.
        """
        try:
            # 메시지 구성
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": img_url},
                        {"type": "text", "text": prompt_text},
                    ],
                }
            ]
            # 채팅 템플릿 적용
            input_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            image_inputs, video_inputs = process_vision_info(messages)

            # 모델 입력 생성
            inputs = processor(
                text=[input_text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            ).to("cuda")

            # 모델 추론
            generated_ids = model.generate(**inputs, max_new_tokens=512)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            return output_text[0]
        except Exception as e:
            print(f"Error processing image at {img_url}: {e}")
            return "Error"

    start_total = time.time()
    for idx, (img_url, product_name) in enumerate(zip(image_urls, product_names)):
        start_time = time.time()

        # 필요한 경우 {product_name} 치환
        prompt = base_prompt.replace("{product_name}", product_name)

        output = process_qwen2_vl(img_url, prompt)
        elapsed_time = time.time() - start_time

        results.append({
            "Model": model_name,
            "ImageURL": img_url,
            "Prompt": prompt,
            "Inference Time (s)": elapsed_time,
            "Model Output": output
        })

        print(f"[Qwen2-VL] {idx+1}/{len(image_urls)} => {elapsed_time:.2f}s => {product_name}")

    total_time = time.time() - start_total
    print(f"[Qwen2-VL] Total time: {total_time:.2f}s")

    # 결과 CSV 저장
    pd.DataFrame(results).to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[Qwen2-VL] Results saved => {output_csv}")