#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[상품 정보 및 리뷰 크롤링 파이프라인]
- 온라인 쇼핑몰에서 상품 정보, 상세 정보, 리뷰 데이터를 수집하는 코드입니다.
- 주요 기능:
  1. get_product_urls: 지정된 카테고리 페이지에서 상품명과 URL 정보를 수집
  2. get_product_details: 각 상품의 상세 페이지에서 정보를 수집
  3. details_to_csv: 수집한 정보를 CSV 파일로 저장
  4. get_product_reviews: 리뷰 데이터를 수집하여 CSV로 저장
"""

import re
import json
import time
import os
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

def get_product_urls(mall_category_url, market="emart", category="아이간식", limit=50):
    BASE_URL = "https://shopping.naver.com"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    all_items = []
    driver.get(mall_category_url)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "_3m7zfsGIZR")))
        except Exception as e:
            print("페이지 로딩 중 오류 발생:", e)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items_list = soup.find_all("li", class_="_3m7zfsGIZR")
        for item in items_list:
            source = item.find("a", class_=re.compile(".*_3OaphyWXEP.*"))
            if source is None:
                continue
            name_dict = json.loads(source["data-shp-contents-dtl"])
            all_items.append({
                "name": name_dict[0]["value"],
                "url": BASE_URL + source["href"],
                "market": market,
                "category": category
            })
        all_items = [dict(i) for i in {frozenset(item.items()) for item in all_items}]
        if len(all_items) >= limit:
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    driver.quit()
    print("상품 총 개수:", len(all_items))
    return all_items

def get_product_details(all_items, limit=50):
    from selenium.webdriver.chrome.options import Options  # 중복 import 방지
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    for item in tqdm(all_items[:limit], desc="상품 상세 정보 수집", total=len(all_items[:limit])):
        driver.get(item["url"])
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "_1Z00EgoxQ9")))
        except Exception as e:
            print("페이지 로딩 중 오류 발생:", e)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            thumbnail_img = soup.find("div", class_="_2tT_gkmAOr").find("img")["src"]
            item["thumbnail"] = thumbnail_img
        except Exception as e:
            item["thumbnail"] = None
        items_list = soup.find_all("span", class_="_1LY7DqCnwR")
        prices = []
        for span in items_list:
            try:
                prices.append(int(span.get_text().replace(",", "")))
            except Exception:
                continue
        if prices:
            if len(prices) > 1:
                item["price"] = {
                    "before_price": max(prices),
                    "after_price": min(prices)
                }
            else:
                item["price"] = {"before_price": prices[0]}
        else:
            item["price"] = {}
        try:
            strong = soup.find("strong", class_="_2pgHN-ntx6")
            star = strong.get_text()[2:]
            item["star"] = float(star)
        except Exception as e:
            item["star"] = None
        sources = soup.find_all("div", class_="_1Z00EgoxQ9")
        imgs = []
        divs = []
        texts = []
        for s in sources:
            imgs = [str(i["src"]) for i in s.find_all("img")]
            divs = [div.get_text() for div in s.find_all("div", class_="tmpl_tit_para")]
            texts = [p.get_text() for p in s.find_all(["h2", "p", "strong", "b"])]
        item["imgs"] = {"num": len(imgs), "urls": imgs}
        item["texts"] = {"num": len(texts), "divs": divs, "contents": texts}
        try:
            item["reviews"] = int(soup.find("span", class_="_3HJHJjSrNK").get_text().replace(",", ""))
        except Exception as e:
            item["reviews"] = 0
            print("리뷰 개수 수집 실패:", item["url"])
        pprint(item)
        print("\n" + "=" * 100 + "\n")
    driver.quit()
    return all_items

def details_to_csv(all_items):
    data_df = pd.DataFrame(columns=["ID", "img-ID", "category", "name", "url", "before_price", "after_price", "star", "thumbnail", "imgs", "texts", "num_reviews"])
    for idx, item in enumerate(all_items[:2]):  # 예제: 2개 상품에 대해 저장
        market = item["market"]
        product_df = pd.DataFrame({
            "ID": f"{market}-{str(idx+1)}",
            "img-ID": f"{market}-{str(idx+1)}-0",
            "category": item["category"],
            "name": item["name"],
            "url": item["url"],
            "before_price": item["price"].get("before_price", None),
            "after_price": item["price"].get("after_price", None),
            "thumbnail": item.get("thumbnail", None),
            "star": item.get("star", None),
            "texts": [str(item.get("texts", {}))],
            "num_reviews": item.get("reviews", 0)
        })
        image_df = pd.DataFrame(columns=["ID", "img-ID", "imgs"])
        for i, img in enumerate(item.get("imgs", {}).get("urls", [])):
            image_df.loc[i] = [f"{market}-{str(idx+1)}", f"{market}-{str(idx+1)}-{str(i+1)}", img]
        product_df = pd.concat([product_df, image_df], axis=0)
        data_df = pd.concat([data_df, product_df], axis=0)
    data_df.to_csv("product_details.csv", index=False)
    print("상세 정보 CSV 저장 완료: product_details.csv")

def get_product_reviews(all_items):
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    review_df = pd.DataFrame(columns=["ID", "review-ID", "category", "name", "url", "meta", "star", "review"])
    for idx, item in enumerate(all_items):
        market = item["market"]
        driver.get(item["url"])
        last_height = driver.execute_script("return document.body.scrollHeight")
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "_11xjFby3Le")))
        except Exception as e:
            print("리뷰 페이지 로딩 중 오류 발생:", e)
        try:
            review_button = driver.find_element(By.XPATH, "//a[contains(text(), '리뷰')]")
            review_button.click()
        except Exception as e:
            print("리뷰 탭 클릭 실패:", e)
            continue
        time.sleep(1)
        meta_dict = {}
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            meta_star = float(soup.find("strong", class_="_2pgHN-ntx6").get_text()[2:])
        except Exception:
            meta_star = None
        meta_keys = [key.get_text() for key in soup.find_all("em", class_="_1ehAE1FZXP")]
        for key in meta_keys:
            try:
                button = driver.find_element(By.XPATH, "//button[contains(@class, '_3pfVLZDLde') and @data-shp-area-id='evalnext']")
                button.click()
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                detail_keys = [key.get_text() for key in soup.find_all("em", class_="_2QT-bjUbDv")]
                detail_values = [int(value.get_text()[:-1]) for value in soup.find_all("span", class_="_1CGcLXygdq")]
                detail_dict = {}
                for d_k, d_v in zip(detail_keys, detail_values):
                    detail_dict[d_k] = d_v
                meta_dict[key] = detail_dict
            except Exception as e:
                continue
        review_meta_df = pd.DataFrame({
            "ID": f"{market}-{str(idx+1)}",
            "review-ID": f"{market}-{str(idx+1)}-0",
            "category": item["category"],
            "name": item["name"],
            "url": item["url"],
            "meta": [str(meta_dict)],
            "star": meta_star,
        })
        try:
            latest_button = driver.find_element(By.XPATH, "//a[text()='최신순']")
            latest_button.click()
            time.sleep(1)
        except Exception as e:
            print("최신순 버튼 클릭 실패:", e)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            review_num = int(soup.find("span", class_="_9Fgp3X8HT7").get_text().replace(",", ""))
        except Exception:
            review_num = 0
        stars = []
        review_texts = []
        for i in range(2):
            try:
                scrollTo = driver.find_element(By.CLASS_NAME, "_1McWUwk15j")
                driver.execute_script("arguments[0].scrollIntoView();", scrollTo)
            except Exception as e:
                pass
            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_divs = soup.find_all("div", class_="_1McWUwk15j")
            for review in review_divs:
                try:
                    star = review.find("em", class_="_15NU42F3kT").get_text()
                    stars.append(star)
                except Exception:
                    stars.append(None)
                try:
                    text_div = review.find("div", class_="_1kMfD5ErZ6").find_all("span")
                    review_texts.append(text_div[-1].get_text())
                except Exception:
                    review_texts.append("")
            try:
                next_page = driver.find_element(By.XPATH, f"//a[contains(@class, 'UWN4IvaQza') and @data-shp-contents-id='{str(i+2)}']")
                next_page.click()
                time.sleep(2)
            except Exception as e:
                break
        review_text_df = pd.DataFrame(columns=["ID", "review-ID", "star", "review"])
        for i, (star, review) in enumerate(zip(stars, review_texts)):
            tmp = pd.DataFrame({
                "ID": f"{market}-{str(idx+1)}",
                "review-ID": f"{market}-{str(idx+1)}-{str(i+1)}",
                "star": [star],
                "review": [review]
            })
            review_text_df = pd.concat([review_text_df, tmp], ignore_index=True)
        reviews = pd.concat([review_meta_df, review_text_df], ignore_index=True)
        review_df = pd.concat([review_df, reviews], ignore_index=True)
    driver.quit()
    return review_df

def run_review_crawling(config):
    print("\n[상품 정보 및 리뷰 크롤링 파이프라인 시작]\n")
    # config에서 크롤링할 상품 수 등 옵션을 읽을 수 있음
    CRAWL_LIMIT = 5
    OUTPUT_FILE = os.path.join(config["paths"]["data_dir"], "product_reviews.csv")
    mall_category_url = "https://shopping.naver.com/best100v2/main.nhn?catId=50000004"
    print("상품 URL 정보 수집 중...")
    product_urls = get_product_urls(mall_category_url, market="emart", category="아이간식", limit=CRAWL_LIMIT)
    print("상품 상세 정보 수집 중...")
    product_details = get_product_details(product_urls, limit=CRAWL_LIMIT)
    print("상품 상세 정보를 CSV로 저장 중...")
    details_to_csv(product_details)
    print("상품 리뷰 수집 중...")
    review_df = get_product_reviews(product_details[:CRAWL_LIMIT])
    review_df.to_csv(OUTPUT_FILE, index=False)
    print("리뷰 정보 CSV 저장 완료:", OUTPUT_FILE)
    print("모든 크롤링 작업 완료되었습니다.")

if __name__ == "__main__":
    run_review_crawling({
        "paths": {
            "data_dir": "./data"
        }
    })
