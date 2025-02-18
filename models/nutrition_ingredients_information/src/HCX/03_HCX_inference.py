import requests
import pandas as pd

import time

class TuningModelInference:
    def __init__(self, host, api_key, request_id, taskId):
        self.host = host
        self.api_key = api_key
        self.request_id = request_id
        self.taskId = taskId

    def infer(self, system_message, user_message):
        headers = {
            'Authorization': self.api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self.request_id,
            'Content-Type': 'application/json; charset=utf-8',
        }

        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.5,
            "topK": 0,
            "topP": 0.8,
            "maxTokens": 1024,
            "repeatPenalty": 5.0,
            "includeAiFilters": True,
            "stopBefore": []
        }

        for attempt in range(20):
            try:
                start_time = time.time()
                with requests.post(self.host + f'/testapp/v2/tasks/{self.taskId}/chat-completions', headers=headers, json=data) as r:
                    elapsed_time = time.time() - start_time
                    response = r.json()

                    # 'status'가 OK이면 'message' 안의 'content'를 추출
                    if response.get("status", {}).get("code") == "20000":
                        return response["result"]["message"]["content"], elapsed_time
                    else:
                        raise ValueError(f"Invalid status code: {response.get('status', {}).get('code')}")
            except (requests.RequestException, ValueError, KeyError) as e:
                if attempt < 20 - 1:
                    print(f"에러 발생: {str(e)}. 10초 후 재시도합니다. (시도 {attempt + 1}/20)")
                    time.sleep(10)
                else:
                    print(f"최대 재시도 횟수 20회를 초과했습니다. 최종 에러: {str(e)}")
                    return None, None

        return None, None

# 파일에서 데이터 읽기
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read().strip()

# CSV에서 OCR 데이터 및 img-ID 로드
def load_ocr_data(csv_filename):
    df = pd.read_csv(csv_filename)
    if 'OCR 결과' not in df.columns or 'img-ID' not in df.columns:
        raise ValueError("CSV 파일에 'OCR 결과' 또는 'img-ID' 열이 없습니다.")
    return df[['img-ID', 'OCR 결과']].to_dict('records')

if __name__ == '__main__':
    # API 인증 정보
    host='https://clovastudio.stream.ntruss.com'
    api_key='YOUR_API_KEY'
    request_id='YOUR_REQUEST_ID'
    taskId = '5s8l73ye'

    # 파일에서 메시지 읽기
    system_message = read_file('prompt/system_prompt_vf.txt')
    user_message_template = read_file('prompt/user_prompt_vf.txt')

    # CSV에서 OCR 데이터 및 img-ID 로드
    ocr_data_list = load_ocr_data('data/OCR/inference/images_323_OCR_row_col.csv')

    # 인퍼런스 실행
    inference = TuningModelInference(host, api_key, request_id, taskId)

    results = []
    for idx, data in enumerate(ocr_data_list):
        img_id = data['img-ID']
        ocr_data = data['OCR 결과']
        
        # OCR 데이터 삽입
        user_message = user_message_template.replace("{ocr_data}", ocr_data)
        
        # API 요청 및 응답 저장
        response_text = inference.infer(system_message, user_message)
        results.append({"img-ID": img_id, "성분정보": response_text})

        # 진행 상황 출력
        print(f"[{idx+1}/{len(ocr_data_list)}] 요청 완료 - img-ID: {img_id}")

    # 결과 저장
    result_df = pd.DataFrame(results)
    result_df.to_csv("data/HCX/inference/HCX_inference_v2.csv", index=False, encoding="utf-8-sig")
