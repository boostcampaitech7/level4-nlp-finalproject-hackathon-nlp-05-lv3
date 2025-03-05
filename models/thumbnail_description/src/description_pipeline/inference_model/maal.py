import os
import time
import re
import requests
import torch
import pandas as pd
import yaml
from PIL import Image

from transformers import MllamaForConditionalGeneration, AutoProcessor
from utils.common_utils import set_seed, load_and_filter_data

def run_inference_maal():
    """
    MAAL 모델 추론 후 CSV 파일에 저장.
    config.yaml을 참고하여 CSV, 프롬프트, 결과 경로를 설정.
    """
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    data_dir   = config["paths"]["data_dir"]        
    prompt_dir = config["paths"]["prompt_dir"]      
    csv_name   = config["paths"]["cleaned_text_contents"]  
    out_name   = config["paths"]["maai_pro_eval"]    

    # 실제 경로 구성
    csv_path    = os.path.join(data_dir, csv_name)           
    prompt_path = os.path.join(prompt_dir, "maal_prompt.txt") 
    output_csv  = os.path.join(data_dir, out_name)            

    # 2) 시드 설정
    set_seed(42)

    # 3) CSV 로드 & 필터링
    df_filtered = load_and_filter_data(csv_path)
    image_urls = df_filtered['url_clean'].to_list()
    product_names = df_filtered['상품명'].to_list()

    # 4) 프롬프트 텍스트 불러오기
    with open(prompt_path, "r", encoding="utf-8") as f:
        base_prompt = f.read().strip()

    # 5) MAAL 모델 준비
    model_id = "maum-ai/Llama-3.2-MAAL-11B-Vision-v0.1"
    print("[MAAL] Loading model...")
    model = MllamaForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    processor = AutoProcessor.from_pretrained(model_id)

    # 모델 output embeddings 조정
    old_embeddings = model.get_output_embeddings()
    num_tokens = model.vocab_size + 1
    resized_embeddings = model._get_resized_lm_head(old_embeddings, new_num_tokens=num_tokens, mean_resizing=True)
    resized_embeddings.requires_grad_(old_embeddings.weight.requires_grad)
    model.set_output_embeddings(resized_embeddings)

    model_name = "maai"
    results = []

    def process_image_with_maai(img_url, prompt):
        try:
            # 이미지 로드 (HTTP GET 후 PIL Image 변환)
            image = Image.open(requests.get(img_url, stream=True).raw)

            # 메시지 구성 (유저 역할에 [이미지 + 텍스트 프롬프트])
            messages = [
                {"role": "user", "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]}
            ]
            # chat 템플릿 적용
            input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
            inputs = processor(
                image,
                input_text,
                add_special_tokens=False,
                return_tensors="pt"
            ).to(model.device)

            # 모델 추론
            output = model.generate(
                **inputs,
                max_new_tokens=256,
                no_repeat_ngram_size=3,
                do_sample=False
            )
            result = processor.decode(output[0])

            # 정규식으로 MAAL 모델 결과에서 assistant 부분 추출
            pattern = r"<\|start_header_id\|>assistant<\|end_header_id\|>\n\n(.+?)(?:<\|eot_id\|>|$)"
            match = re.search(pattern, result, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return "No match found"
        except Exception as e:
            print(f"Error processing image at {img_url}: {e}")
            return "Error"

    # 6) 각 이미지에 대해 추론 수행
    for idx, (image_url, product_name) in enumerate(zip(image_urls, product_names)):
        start_time = time.time()
        # prompt에 {product_name} 치환 (필요 시)
        prompt = base_prompt.replace("{product_name}", product_name)

        output = process_image_with_maai(image_url, prompt)
        elapsed_time = time.time() - start_time

        results.append({
            "Model": model_name,
            "ImageURL": image_url,
            "Prompt": prompt[:100],  # 길이 제한
            "Inference Time (s)": elapsed_time,
            "Model Output": output
        })

        print(f"[MAAL] Processed {idx+1}/{len(image_urls)} => {elapsed_time:.2f}s => {product_name}")

    # 7) 결과를 CSV로 저장
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[MAAL] Results saved => {output_csv}")