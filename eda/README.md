# 데이터 수집 및 EDA

- 네이버 쇼핑 > 장보기탭 > 주요 쇼핑몰의 식료품 데이터를 수집해서 EDA 수행
- EDA 결과를 바탕으로 프로젝트에 기반이 되는 파이프라인, 데이터별 AI 기술 매칭 가이드 구축

## 주요 특징

- **데이터 수집:**  
  `product_crawling.py`를 이용해서 네이버 쇼핑의 특정 카테고리 페이지에서 상품 URL, 이름, 마켓, 카테고리 등 기본 정보를 수집하고, 각 상품의 상세 페이지에서 썸네일, 가격, 별점, 상세 이미지 및 텍스트, 리뷰 개수 등의 정보를 추출

- **EDA 수행:**  
  수집한 데이터를 기반으로  
  - `eda1_visualize.ipynb`: 1차 EDA를 통해 각 마켓별 정보 제공 방식과 형태를 파악
  - `eda2_visualization.ipynb`: 2차 EDA를 통해 상품 상세 설명의 정형화 여부 및 서비스 개발을 위한 AI 기술 매칭 가이드를 도출

- **파이프라인 기반 데이터셋 구축:**  
  - 크롤링과 EDA 결과를 활용해서 현재 프로젝트의 핵심 파이프라인에 기반이 되는 데이터셋을 완성

## 폴더 구조
```bash
.
├── product_crawling.py         # 데이터 크롤링 및 상품 상세 정보 추출 스크립트
├── eda1_visualize.ipynb        # 1차 EDA 및 시각화 노트북
├── eda2_visualization.ipynb    # 2차 EDA 및 시각화 노트북
└── README.md                   # 프로젝트 문서
```

## 설치 및 실행 방법

1. **패키지 설치**  
   ```bash
   pip install ipywidgets webdriver-manager beautifulsoup4 selenium tqdm
   ```  

2. **데이터 수집**  
   ```bash
   python product_crawling.py
   ```

3. **EDA**  
  - Google Sheets를 활용하여 수동 레이블링 검수가 완료된 `.csv` 파일 필요
  - eda1_visualize.ipynb: 1차 EDA와 기본 시각화 결과 확인
  - eda2_visualization.ipynb: 2차 EDA를 통한 정형화 여부 확인 및 AI 기술 매칭 가이드 도출  

## 추가 정보
- **동적 페이지 로딩:**  
   크롤링 과정에서 페이지 스크롤과 동적 로딩을 고려했으므로, 네이버 쇼핑 페이지 구조 변경 시 코드 업데이트가 필요할 수 있음
- **향후 계획:**  
   EDA 결과를 바탕으로 시각장애인을 위한 온라인 쇼핑 접근성 개선 및 AI 기술 적용에 관한 구체적인 파이프라인을 개발 예정
