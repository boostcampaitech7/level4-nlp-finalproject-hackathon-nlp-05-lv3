import os
import time
import urllib.request
import pandas as pd
import torch
import yaml

from transformers import AutoModelForCausalLM
from janus.models import MultiModalityCausalLM, VLChatProcessor
from janus.utils.io import load_pil_images

from utils.common_utils import set_seed, load_and_filter_data

def run_inference_janus_pro():
    """
    itsmenlp/finetuned-Janus-Pro-7B 모델 추론 후 결과 CSV 저장.
    config.yaml을 참고하여 CSV, 프롬프트, 결과 경로를 설정.
    """
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    data_dir = config["paths"]["data_dir"]          
    prompt_dir = config["paths"]["prompt_dir"]      
    csv_name = config["paths"]["cleaned_text_contents"]   
    out_name = config["paths"]["janus_pro_eval"]    
    
    # 실제 경로 구성
    csv_path = os.path.join(data_dir, csv_name)           
    prompt_path = os.path.join(prompt_dir, "janus_prompt.txt") 
    output_csv = os.path.join(data_dir, out_name)         

    # 2) 시드 설정
    set_seed(42)

    # 3) CSV 로드 & 필터링
    df_filtered = load_and_filter_data(csv_path)
    image_urls = df_filtered['url_clean'].to_list()
    product_names = df_filtered['상품명'].to_list()

    # 4) 프롬프트 텍스트 읽기
    with open(prompt_path, "r", encoding="utf-8") as f:
        base_prompt = f.read().strip()

    # 5) Janus-Pro 모델 준비
    model_path = "itsmenlp/finetuned-Janus-Pro-7B" #private
    vl_chat_processor = VLChatProcessor.from_pretrained(model_path)
    tokenizer = vl_chat_processor.tokenizer

    vl_gpt = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True)
    vl_gpt = vl_gpt.to(torch.bfloat16).cuda().eval()

    model_name = "itsmenlp/finetuned-Janus-Pro-7B"

    def process_image(img_url, prompt):
        temp_filename = "temp_janus.jpg"
        urllib.request.urlretrieve(img_url, temp_filename)
        try:
            conversation = [
                {"role": "<|User|>", "content": f"<image_placeholder>\n{prompt}", "images": [temp_filename]},
                {"role": "<|Assistant|>", "content": ""}
            ]
            pil_images = load_pil_images(conversation)
            prepare_inputs = vl_chat_processor(
                conversations=conversation, images=pil_images, force_batchify=True
            ).to(vl_gpt.device)

            inputs_embeds = vl_gpt.prepare_inputs_embeds(**prepare_inputs)
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
            return answer
        except Exception as e:
            print(f"Error processing image at {img_url}: {e}")
            return "Error: An unexpected error occurred."
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    # 6) 반복 추론
    results = []
    for idx, (image_url, product_name) in enumerate(zip(image_urls, product_names)):
        start_time = time.time()
        prompt = base_prompt

        output = process_image(image_url, prompt)
        elapsed_time = time.time() - start_time

        results.append({
            "Model": model_name,
            "ImageURL": image_url,
            "Prompt": prompt,
            "Inference Time (s)": elapsed_time,
            "Model Output": output
        })

        print(f"[JanusPro] Processed {idx+1}/{len(image_urls)} in {elapsed_time:.2f}s => {product_name}")

    # 7) 결과 저장
    pd.DataFrame(results).to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[JanusPro] Saved results => {output_csv}")