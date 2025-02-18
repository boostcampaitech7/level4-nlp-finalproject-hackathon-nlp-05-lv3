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
                url = self._host + '/testapp/v1/chat-completions/HCX-003'
                response = requests.post(url, headers=headers, json=completion_request)
                response_data = response.json()

                if response_data.get("status", {}).get("code") == "20000":
                    return response_data["result"]["message"]["content"]
                else:
                    raise ValueError(f"Invalid status code: {response_data.get('status', {}).get('code')}")
            except (requests.RequestException, ValueError, KeyError) as e:
                if attempt < max_retries - 1:
                    print(f"에러 발생: {str(e)}. {retry_delay}초 후 재시도합니다. (시도 {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"최대 재시도 횟수 {max_retries}회를 초과했습니다. 최종 에러: {str(e)}")
                    return None

def main():
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # HCX API 정보 가져오기
    host = config_data["hcx_api"]["host"]
    api_key = config_data["hcx_api"]["api_key"]
    request_id = config_data["hcx_api"]["request_id"]

    # paths 섹션에서 경로 가져오기
    data_dir = config_data["paths"]["data_dir"]               
    hcx_prompt_dir = config_data["paths"].get("hcx_prompt_dir", "hcx_prompt")  
    csv_name = config_data["paths"].get("qwen2_5+janus_323_eval", "qwen2_5+janus_323_eval.csv")
    
    # 실제 CSV 경로 구성
    csv_path = os.path.join(data_dir, csv_name)
    
    # prompt 파일 경로 구성
    system_prompt_path = os.path.join(hcx_prompt_dir, "system_janus_pro_hcx_translation.txt")
    user_prompt_path   = os.path.join(hcx_prompt_dir, "user_janus_pro_hcx_translation.txt")

    completion_executor = CompletionExecutor(host, api_key, request_id)

    # system / user prompt 파일 불러오기
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()

    with open(user_prompt_path, "r", encoding="utf-8") as f:
        user_prompt_template = f.read().strip()

    # CSV 로드
    df = pd.read_csv(csv_path)

    # 각 행에 대해 추론 실행
    for idx, row in df.iterrows():
        # "Model Output" 칼럼에서 텍스트 가져오기
        model_output_text = row.get("Model Output", "")

        # user 프롬프트 생성
        user_prompt = user_prompt_template.replace("{model_output_text}", model_output_text)

        request_data = {
            'messages': [
                {"role": "system", "content": system_prompt},
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

        # HCX 모델 호출
        model_output_ko = completion_executor.execute(request_data)
        df.loc[idx, "Model Output HCX"] = model_output_ko

        print(idx, model_output_ko)

    # 결과 저장 (덮어쓰기)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[janus_pro_hcx_translation] 파일 저장 완료: {csv_path}")

if __name__ == "__main__":
    main()