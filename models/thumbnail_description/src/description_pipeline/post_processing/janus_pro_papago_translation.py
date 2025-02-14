from utils.common_utils import (
    set_seed, requests, pd
)
import yaml

def translate_text(text, source_lang, target_lang, client_id, client_secret):
    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
    headers = {
        "x-ncp-apigw-api-key-id": client_id,
        "x-ncp-apigw-api-key": client_secret
    }
    data = {
        "source": source_lang,
        "target": target_lang,
        "text": text
    }

    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code == 200:
        js = resp.json()
        return js['message']['result']['translatedText']
    else:
        print(f"Papago Error Code: {resp.status_code}")
        return None

def main():
    # config.yaml에서 Papago API 정보 로드
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    client_id = cfg["papago_api"]["client_id"]
    client_secret = cfg["papago_api"]["client_secret"]

    csv_path = "qwen2_5+janus_323_eval.csv"
    df = pd.read_csv(csv_path)

    # Model Output 열 영어를 한국어로 번역
    df["Model Output Papago"] = df["Model Output"].apply(
        lambda x: translate_text(str(x), "en", "ko", client_id, client_secret)
    )

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[papago_translation] 번역 완료 => {csv_path}")

if __name__ == "__main__":
    main()