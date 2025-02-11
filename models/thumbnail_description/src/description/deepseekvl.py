import os
import time
import urllib.request
import pandas as pd
import torch
import yaml

from transformers import AutoModelForCausalLM
from deepseek_vl.models import VLChatProcessor, MultiModalityCausalLM
from deepseek_vl.utils.io import load_pil_images

from utils.common_utils import set_seed, load_and_filter_data

def run_inference_deepseekvl():
    """
    DeepSeek-VL-7B-Chat 모델을 활용한 추론 스크립트.
    config.yaml을 통해 CSV 경로, 프롬프트 경로, 결과 저장 경로를 읽어온 뒤 작업 수행.
    """
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    data_dir   = config["paths"]["data_dir"]          
    prompt_dir = config["paths"]["prompt_dir"]        
    csv_name   = config["paths"]["cleaned_text_contents"]  
    out_name   = config["paths"]["deepseekvl_eval"]   

    # 실제 경로 구성
    csv_path    = os.path.join(data_dir, csv_name)    
    prompt_path = os.path.join(prompt_dir, "deepseek_prompt.txt") 
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

    # 5) DeepSeek 모델 준비
    model_path = "deepseek-ai/deepseek-vl-7b-chat"
    vl_chat_processor = VLChatProcessor.from_pretrained(model_path)
    tokenizer = vl_chat_processor.tokenizer

    vl_gpt = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True)
    vl_gpt = vl_gpt.to(torch.bfloat16).cuda().eval()

    model_name = "deepseek-ai/deepseek-vl-7b-chat"

    def process_image(image_url, prompt):
        """
        개별 이미지 URL에 대해 DeepSeek-VL 모델 추론을 수행하는 내부 함수.
        """
        # 임시 다운로드 파일명
        temp_filename = "temp_deepseek.jpg"

        # 이미지 다운로드
        urllib.request.urlretrieve(image_url, temp_filename)
        try:
            # 대화 데이터 구성
            conversation = [
                {
                    "role": "User",
                    "content": f"<image_placeholder>\n{prompt}",
                    "images": [temp_filename]
                },
                {
                    "role": "Assistant",
                    "content": ""
                }
            ]
            # 이미지 로드
            pil_images = load_pil_images(conversation)

            # 입력 준비
            prepare_inputs = vl_chat_processor(
                conversations=conversation, images=pil_images, force_batchify=True
            ).to(vl_gpt.device)

            # 이미지 임베딩
            inputs_embeds = vl_gpt.prepare_inputs_embeds(**prepare_inputs)

            # 텍스트 생성
            outputs = vl_gpt.language_model.generate(
                inputs_embeds=inputs_embeds,
                attention_mask=prepare_inputs.attention_mask,
                pad_token_id=tokenizer.eos_token_id,
                bos_token_id=tokenizer.bos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.2,
                top_p=0.95
            )
            answer = tokenizer.decode(outputs[0].cpu().tolist(), skip_special_tokens=True)

            print(f"{prepare_inputs['sft_format'][0]}", answer)
            return answer
        except Exception as e:
            print(f"Error processing image at {image_url}: {e}")
            return "Error: An unexpected error occurred."
        finally:
            # 다운로드 파일 삭제(필요 시)
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    # 6) 반복 추론
    results = []
    for idx, (image_url, product_name) in enumerate(zip(image_urls, product_names)):
        start_time = time.time()

        prompt = base_prompt

        output = process_image(image_url, prompt)
        elapsed = time.time() - start_time

        results.append({
            "Model": model_name,
            "ImageURL": image_url,
            "Prompt": prompt,
            "Inference Time (s)": elapsed,
            "Model Output": output
        })

        print(f"[{idx+1}/{len(image_urls)}] Processed in {elapsed:.2f}s => {product_name}")

    # 7) 결과 저장
    pd.DataFrame(results).to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[DeepSeek-VL] Saved results => {output_csv}")