import time
import requests

# HCX-003 기본 모델
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
                start_time = time.time()
                with requests.post(
                    self._host + '/testapp/v1/chat-completions/HCX-003',
                    headers=headers, json=completion_request
                ) as r:
                    elapsed_time = time.time() - start_time
                    response = r.json()

                    if response.get("status", {}).get("code") == "20000":
                        return response["result"]["message"]["content"], elapsed_time
                    else:
                        raise ValueError(f"Invalid status code: {response.get('status', {}).get('code')}")
            except (requests.RequestException, ValueError, KeyError) as e:
                if attempt < max_retries - 1:
                    print(f"에러 발생: {str(e)}. {retry_delay}초 후 재시도합니다. (시도 {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"최대 재시도 횟수 {max_retries}회를 초과했습니다. 최종 에러: {str(e)}")
                    return None, None

        return None, None


# 학습 생성
class CreateTaskExecutor:
    def __init__(self, host, uri, api_key, request_id):
        self._host = host
        self._uri = uri
        self._api_key = api_key
        self._request_id = request_id

    def _send_request(self, create_request):
        headers = {
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }
        result = requests.post(self._host + self._uri, json=create_request, headers=headers).json()
        return result

    def execute(self, create_request):
        res = self._send_request(create_request)
        if 'status' in res and res['status']['code'] == '20000':
            return res['result']
        else:
            return res


# 튜닝된 HCX-003 모델
class FinetunedCompletionExecutor:
    def __init__(self, host, api_key, request_id, taskId):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id
        self._taskID = taskId

    def execute(self, completion_request, max_retries=5, retry_delay=20):
        headers = {
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
        }
    
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                with requests.post(
                    self._host + f'/testapp/v2/tasks/{self._taskID}/chat-completions',
                    headers=headers, json=completion_request
                ) as r:
                    elapsed_time = time.time() - start_time
                    response = r.json()

                    if response.get("status", {}).get("code") == "20000":
                        return response["result"]["message"]["content"], elapsed_time
                    else:
                        raise ValueError(f"Invalid status code: {response.get('status', {}).get('code')}")
            except (requests.RequestException, ValueError, KeyError) as e:
                if attempt < max_retries - 1:
                    print(f"에러 발생: {str(e)}. {retry_delay}초 후 재시도합니다. (시도 {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"최대 재시도 횟수 {max_retries}회를 초과했습니다. 최종 에러: {str(e)}")
                    return None, None

        return None, None
