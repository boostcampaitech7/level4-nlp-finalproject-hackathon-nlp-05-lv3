import time
import logging
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def run_text_crawling(config):
    """
    상품별 텍스트 크롤링을 수행하고, 
    결과를 total_text.csv로 저장하는 함수.
    """
    data_dir = config["paths"]["data_dir"]
    total_csv = config["paths"]["total_csv"]
    total_text_csv = config["paths"]["total_text_csv"]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 최대 재시도 횟수 지정
    max_retries = 3

    # 데이터 목록 불러오기
    data_path = f"{data_dir}/{total_csv}"
    data = pd.read_csv(data_path)

    # 상품별 텍스트 크롤링
    for idx, row in data.iterrows():
        url = row['상품 상세 URL']
        retry_count = 0  # 재시도 횟수 초기화

        while retry_count < max_retries:
            try:
                driver.get(url)
                
                # 상세 정보 페이지 로딩이 완료될 때까지 대기
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "_1Z00EgoxQ9")))

                # 크롤링
                soup = BeautifulSoup(driver.page_source, "html.parser")
                sources = soup.find_all("div", class_="_1Z00EgoxQ9")  # 상세 정보 탐색 범위

                divs, texts = [], []
                for s in sources:
                    divs = [div.get_text() for div in s.find_all("div", class_="tmpl_tit_para")]
                    texts = [p.get_text() for p in s.find_all(["h2", "p", "strong", "b"])]  # 찾고 싶은 텍스트 태그 지정, <div> 태그로 감싸진 텍스트는 가져오지 않음

                result = {"num": len(texts), "divs": divs, "contents": texts}
                data.loc[idx, '텍스트'] = str(result)
                print(idx, result)
                print("-" * 100)
                time.sleep(3)
                break

            except Exception as e:
                print(f"페이지 로딩/크롤링 중 오류 발생 (시도 {retry_count+1}/{max_retries}): {e}")
                retry_count += 1
                time.sleep(3)  # 재시도 전 대기

                if retry_count == max_retries:
                    data.loc[idx, '텍스트'] = ""
                    print(f"URL {url} 크롤링 실패, 다음 URL로 이동")

    driver.quit()

    output_path = f"{data_dir}/{total_text_csv}"
    data.to_csv(output_path, index=False)
    logger.info(f"크롤링 결과가 {output_path} 에 저장되었습니다.")
