from utils.common_utils import (
    set_seed, requests, pd, time
)
import yaml

class CompletionExecutor:
    def __init__(self, host, api_key, request_id):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id

    def execute(self, completion_request, max_retries=5, retry_delay=20):
        headers = {
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
        }
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self._host + '/testapp/v1/chat-completions/HCX-003',
                    headers=headers, json=completion_request
                )
                data = response.json()

                if data.get("status", {}).get("code") == "20000":
                    return data["result"]["message"]["content"]
                else:
                    raise ValueError(f"Invalid status code: {data.get('status', {}).get('code')}")
            except (requests.RequestException, ValueError, KeyError) as e:
                if attempt < max_retries - 1:
                    print(f"에러 발생: {str(e)}. {retry_delay}초 후 재시도 (시도 {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"최대 재시도 횟수 {max_retries}회 초과. 최종 에러: {str(e)}")
                    return None

def main():
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # HCX API 정보
    host = config["hcx_api"]["host"]
    api_key = config["hcx_api"]["api_key"]
    request_id = config["hcx_api"]["request_id"]

    # data_dir & prompt_dir 등 가져오기
    data_dir   = config["paths"]["data_dir"]   
    prompt_dir = config["paths"]["prompt_dir"]

    # Foodly_323_product_information.csv 경로
    csv_name = config["paths"]["Foodly_323_product_information"]  
    csv_path = os.path.join(data_dir, csv_name)                   

    # system / user 프롬프트 파일 경로
    system_prompt_path = os.path.join(prompt_dir, "system_janus_pro_hcx_fewshot.txt")
    user_prompt_path   = os.path.join(prompt_dir, "user_janus_pro_hcx_fewshot.txt")

    completion_executor = CompletionExecutor(host, api_key, request_id)

    # CSV 파일 로드
    df = pd.read_csv(csv_path)

    # system / user prompt 불러오기
    with open(system_prompt_path, "r", encoding="utf-8") as sf:
        system_prompt_fewshot = sf.read().strip()

    with open(user_prompt_path, "r", encoding="utf-8") as uf:
        user_prompt_template_fewshot = uf.read().strip()

    # 시드 설정
    set_seed(42)

    # 3) 각 행에 대해 HCX 모델 호출
    for idx, row in df.iterrows():
        model_output_text = row.get("Janus_Pro_Model_Output", "")
        # user 프롬프트에 CSV에서 가져온 텍스트를 치환
        user_prompt = user_prompt_template_fewshot.replace("{model_output_text}", model_output_text)

        request_data = {
            "messages": [
                {"role": "system", "content": system_prompt_fewshot},
                {"role": "user", "content": user_prompt}
            ],
            'topP': 0.9,
            'topK': 0,
            'maxTokens': 1024,
            'temperature': 0.1,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 42
        }

        result_ko = completion_executor.execute(request_data)
        df.loc[idx, "Janus_Pro_Model_Output_HCX"] = result_ko

        print(idx, result_ko)

    # 4) 결과 CSV 저장 (같은 파일에 덮어쓰기)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[fewshot_janus_pro_hcx] 파일 저장 완료 => {csv_path}")

if __name__ == "__main__":
    main()