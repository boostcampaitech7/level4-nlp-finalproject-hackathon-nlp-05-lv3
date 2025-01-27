import os
import time
import re
import yaml
import pandas as pd
import torch
import requests
from PIL import Image
from unsloth import FastVisionModel
from transformers import TextStreamer
from qwen_vl_utils import process_vision_info

from utils.common_utils import set_seed, load_and_filter_data

def run_inference_unsloth_qwen2_vl():
    """
    unsloth 기반 Qwen2-VL 모델 추론.
    config.yaml을 통해 CSV, 프롬프트, 결과 경로를 설정해 실행.
    """
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    data_dir   = config["paths"]["data_dir"]            
    prompt_dir = config["paths"]["prompt_dir"]           
    csv_name   = config["paths"]["cleaned_text_contents"]  
    out_name   = config["paths"]["unsloth_qwen2_eval"]   

    # 실제 경로 구성
    csv_path    = os.path.join(data_dir, csv_name)                  
    prompt_path = os.path.join(prompt_dir, "unsloth_prompt.txt")    
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

    # 5) unsloth 기반 Qwen2-VL 모델 로딩
    print("[unsloth] Loading Qwen2-VL-7B-Instruct model...")
    model, tokenizer = FastVisionModel.from_pretrained(
        "unsloth/Qwen2-VL-7B-Instruct",
        load_in_4bit=False,
        use_gradient_checkpointing="True",
        trust_remote_code=True,
    )

    # LoRA 설정 등
    model = FastVisionModel.get_peft_model(
        model,
        finetune_vision_layers=True,
        finetune_language_layers=True,
        finetune_attention_modules=True,
        finetune_mlp_modules=True,
        r=16,
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        random_state=3407,
        use_rslora=False,
        loftq_config=None
    )
    FastVisionModel.for_inference(model)

    # 이미지 크기 설정
    min_pixels = 256 * 28 * 28
    max_pixels = 960 * 28 * 28
    model_name = "qwen_unsloth"
    results = []

    def process_single_image(img_url, product_name):
        """
        단일 이미지 URL과 product_name으로 모델 추론 실행.
        """
        start_time = time.time()

        prompt_text = base_prompt.replace("{product_name}", product_name)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": img_url,
                        "min_pixels": min_pixels,
                        "max_pixels": max_pixels,
                    },
                    {"type": "text", "text": prompt_text}
                ]
            }
        ]
        input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)

        # 입력 텐서 생성
        inputs = tokenizer(
            image_inputs,
            input_text,
            add_special_tokens=False,
            return_tensors="pt",
        ).to("cuda")

        # 모델 추론
        output_ids = model.generate(
            **inputs,
            max_new_tokens=256,
            use_cache=True,
            temperature=1.5,
            min_p=0.1
        )
        output_texts = tokenizer.batch_decode(
            output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        # assistant\n (텍스트) 정규표현식으로 추출
        pattern = r'assistant\n(.+)'
        matches = re.findall(pattern, output_texts[0], re.DOTALL)
        final_output = matches[0] if matches else "No valid output generated"

        elapsed = time.time() - start_time
        return final_output, elapsed

    # 6) 각 이미지에 대해 추론
    for idx, (img_url, prod_name) in enumerate(zip(image_urls, product_names)):
        caption, elapsed_time = process_single_image(img_url, prod_name)
        results.append({
            "Model": model_name,
            "ImageURL": img_url,
            "Product Name": prod_name,
            "Inference Time (s)": elapsed_time,
            "Model Output": caption
        })
        print(f"[unsloth Qwen2-VL] {idx+1}/{len(image_urls)} => {elapsed_time:.2f}s => {prod_name}")

    # 7) 결과 CSV 저장
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[unsloth Qwen2-VL] Saved results => {output_csv}")