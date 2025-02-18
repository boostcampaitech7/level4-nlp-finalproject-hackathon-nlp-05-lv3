import re
import json
import time
import pandas as pd
from tqdm import tqdm
from pprint import pprint

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


def get_product_urls(mall_category_url, market, category, limit):
    """
    카테고리 페이지에서 상품의 이름과 url 정보를 수집하는 함수
    
    :param mall_category_url: 마켓의 특정 카테고리 페이지 (ex. 이마트몰의 과일 카테고리)
    :param market: 지정한 카테고리 이름
    :return: 상품명, url, 카테고리 정보가 포함된 dict
    """

    BASE_URL = "https://shopping.naver.com"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    all_items = []

    driver.get(mall_category_url)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 페이지가 전부 로드될 때까지 대기
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "_3m7zfsGIZR")))
        except Exception as e:
            print("페이지 로딩 중 오류 발생:", e)

        # 시작
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items_list = soup.find_all("li", class_="_3m7zfsGIZR")
        for item in items_list:
            source = item.find("a", class_=re.compile(".*_3OaphyWXEP.*"))
            name_dict = json.loads(source["data-shp-contents-dtl"])
            all_items.append({
                "name": name_dict[0]["value"],
                "url": BASE_URL + source["href"],
                "market": market,
                "category": category
            })

        # 중복 제거 후 개수 세기    
        all_items = [dict(i) for i in {frozenset(item.items()) for item in all_items}]    
        if len(all_items) >= limit: break

        # 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        # 페이지 최하단인지 확인
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.quit()

    print("상품 총 개수:", len(all_items))
    return all_items


def get_product_details(all_items, limit, output_name):
    """
    get_product_urls의 결과로 반환된 dict를 통해 상품의 상세 정보를 수집하는 함수
    - 썸네일 이미지 주소
    - 가격(할인 전, 후)
    - 별점
    - 상품 상세 이미지 주소들
    - 상품 상세 텍스트들
    - 총 리뷰 개수
    
    :param all_items: get_product_urls 결과 반환된 dict
    :param limit: 가져올 상품의 개수이며, len(all_items)를 초과할 수 없음
    :output_name: 데이터 프레임으로 저장할 파일 경로 및 이름
    :return: 입력으로 받은 dict에 상품 상세 정보가 추가된 dict
    """

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    for item in tqdm(all_items[:limit], desc="product meta", total=len(all_items[:limit])): # 여기 주석 해제하고 아래 line 주석 처리하면 모든 상품 대상으로 조회 가능
        driver.get(item["url"])

        # 상세 정보 페이지 로딩이 완료될 때까지 대기
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "_1Z00EgoxQ9")))
        except Exception as e:
            print("페이지 로딩 중 오류 발생:", e)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # 썸네일
        thumbnail_img = soup.find("div", class_="_2tT_gkmAOr").find("img")["src"]
        item["thumbnail"] = thumbnail_img

        # 가격
        items_list = soup.find_all("span", class_="_1LY7DqCnwR")
        prices = [int(item.get_text().replace(",", "")) for item in items_list]
        if len(prices) > 1:
            item["price"] = {
                "before_price": max(prices),
                "after_price": min(prices)
            }
        else:
            item["price"] = {"before_price": prices[0]}
        
        # 별점
        strong = soup.find("strong", class_="_2pgHN-ntx6")
        star = strong.get_text()[2:]
        item["star"] = float(star)

        # 상세 이미지, 텍스트, 총 리뷰 개수
        sources = soup.find_all("div", class_="_1Z00EgoxQ9")
        imgs = []
        for s in sources:
            imgs = [str(i["src"]) for i in s.find_all("img")] # 상세 이미지
            divs = [divs.get_text() for divs in s.find_all("div", class_="tmpl_tit_para")] # 텍스트 - div
            texts = [p.get_text() for p in s.find_all(["h2", "p", "strong", "b"])] # 텍스트 - h2, p, strong, b (수정 가능)
        item["imgs"] = {"num": len(imgs), "urls": imgs}
        item["texts"] = {"num": len(texts), "divs": divs, "contents": texts}
        try:
            item["reviews"] = int(soup.find("span", class_="_3HJHJjSrNK").get_text().replace(",", ""))
        except Exception as e:
            item["reviews"] = 0
            print("passed...", item["url"])
        pprint(item)
        print("\n============================================================================================\n")

    driver.quit()

    ##### DataFrame 변환, csv로 저장
    data_df = pd.DataFrame(columns=["ID", "img-ID", "category", "name", "url", "before_price", "after_price", "star", "thumbnail", "imgs", "texts", "num_reviews"])

    for idx, item in enumerate(all_items[:2]):
        market = item["market"]

        product_df = pd.DataFrame({
            "ID": f"{market}-{str(idx+1)}",
            "img-ID": f"{market}-{str(idx+1)}-0",
            "category": item["category"],
            "name": item["name"],
            "url": item["url"],
            "before_price": item["price"]["before_price"],
            "after_price": item["price"]["after_price"] if "after_price" in item["price"] else None,
            "thumbnail": item["thumbnail"],
            "star": item["star"],
            "texts": [str(item["texts"])],
            "num_reviews": item["reviews"]
        })

        image_df = pd.DataFrame(columns=["ID", "img-ID", "imgs"])
        for i, img in enumerate(item["imgs"]["urls"]):
            image_df.loc[i] = [f"{market}-{str(idx+1)}", f"{market}-{str(idx+1)}-{str(i+1)}", img]
        
        product_df = pd.concat([product_df, image_df])
        data_df = pd.concat([data_df, product_df])

    data_df.to_csv(output_name, index=False)

    return all_items


if __name__ == "__main__":
    LIMIT = 50
    all_items = get_product_urls(mall_category_url="", market="emart", category="아이간식", limit=LIMIT)
    get_product_details(all_items, limit=LIMIT, output_name="./product_details.csv")
