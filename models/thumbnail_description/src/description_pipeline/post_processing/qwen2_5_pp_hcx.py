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
            'Content-Type': 'application/json; charset=utf-8'
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
                    print(f"에러 발생: {str(e)}. {retry_delay}초 후 재시도. (시도 {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"최대 재시도 횟수 {max_retries}회 초과. 최종 에러: {str(e)}")
                    return None

def main():
    # 1) config.yaml 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    host = cfg["hcx_api"]["host"]
    api_key = cfg["hcx_api"]["api_key"]
    request_id = cfg["hcx_api"]["request_id"]

    completion_executor = CompletionExecutor(host, api_key, request_id)

    # 2) system / user prompt를 파일에서 불러오기
    with open("hcx_prompt/system_qwen2_5_pp_hcx.txt", "r", encoding="utf-8") as sf:
        system_prompt = sf.read().strip()

    with open("hcx_prompt/user_qwen2_5_pp_hcx.txt", "r", encoding="utf-8") as uf:
        user_prompt_template = uf.read().strip()

    # 3) CSV 로드
    csv_path = "qwen2.5_323_eval.csv"
    df = pd.read_csv(csv_path)

    # 시드 설정
    set_seed(42)

    # 4) 각 행별로 HCX 요청
    for idx, row in df.iterrows():
        model_output_text = row.get("Model Output", "")

        # user prompt 구성
        user_prompt = user_prompt_template.replace("{model_output_text}", model_output_text)

        request_data = {
            "messages": [
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

        model_output_HCX_PP = completion_executor.execute(request_data)
        df.loc[idx, "Model Output HCX PP"] = model_output_HCX_PP
        print(idx, model_output_HCX_PP)

    # 5) CSV 저장
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[qwen2_5_pp_hcx] 파일 저장 완료 => {csv_path}")

if __name__ == "__main__":
    main()