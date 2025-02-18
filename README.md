<div align='center'>

# [Lv. 4] 기업연계해커톤 - 네이버 클라우드  

## 🛍️ Foodly (시각장애인을 위한 식료품 쇼핑 서비스)

<img width="960" alt="image" src="https://github.com/user-attachments/assets/7dea288d-9732-4243-a168-71902bc381eb" />


</div>

## 🏃 프로젝트 설명

### 🖥️ 프로젝트 개요

<div align="center">
<video src="./doc/image/demo.mp4" width="200" autoplay loop muted></video>
</div>

| 특징　　　　| 설명 |
|:------:| --- |
| 주제 | 시각장애인을 위한 온라인 식료품 쇼핑 지원 서비스입니다. |
| 문제 정의 | 온라인 쇼핑은 대부분의 사람들에게 편리한 과정이지만, 시각장애인에게는 화면의 모든 내용을 음성으로 듣고 정보를 찾는 데 많은 시간이 필요합니다. 특히, 상품의 성분/영양 정보와 알레르기 정보 등 이미지로 제공되는 정보를 확인하는 과정에서 어려움을 겪고 있습니다. |
| 기능 | - 상품 대표 이미지(썸네일)를 텍스트로 변환하여 전달 <br> - 상품의 크기 정보, 보관법, 성분/영양 정보 등의 상세 정보를 직관적인 텍스트로 제공 <br> - 리뷰 긍·부정 의견 요약, 키워드 기반 상품 추천 시스템 개발 |
| 결과물 | [WrapUp Report](https://github.com/boostcampaitech7/level4-nlp-finalproject-hackathon-nlp-05-lv3/blob/main/doc/네이버클라우드_NLP_팀%20리포트(05조)%20(1).pdf), [Presentation Material](https://github.com/boostcampaitech7/level4-nlp-finalproject-hackathon-nlp-05-lv3/blob/main/doc/NLP_5조_네이버%20클라우드_푸드리%20(1).pdf) |

<br>

### 💡 전체 파이프라인
<img width="960" alt="image" src="https://github.com/user-attachments/assets/4aea48ee-382d-421c-8afc-30ca42bcc03d" />


### ✅ 시각장애인 7분의 푸드리 사용성 평가
<img width="960" alt="스크린샷 2025-02-18 오후 9 01 07" src="https://github.com/user-attachments/assets/d2c5f581-cb94-4490-b67c-b10699121377" />


<br>

<br>

## 🐟 "나야, 자, 연어"팀 멤버 소개
| 곽희준&nbsp; [<picture><source media="(prefers-color-scheme: light)" srcset="./doc/image/github_dark.png" /><source media="(prefers-color-scheme: dark)" srcset="./doc/image/github_light.png" /><img src="./doc/image/github_dark.png" height="20" /></picture>](https://github.com/gwaksital) | 김정은&nbsp; [<picture><source media="(prefers-color-scheme: light)" srcset="./doc/image/github_dark.png" /><source media="(prefers-color-scheme: dark)" srcset="./doc/image/github_light.png" /><img src="./doc/image/github_dark.png" height="20" /></picture>](https://github.com/wjddms4299) | 김진재&nbsp; [<picture><source media="(prefers-color-scheme: light)" srcset="./doc/image/github_dark.png" /><source media="(prefers-color-scheme: dark)" srcset="./doc/image/github_light.png" /><img src="./doc/image/github_dark.png" height="20" /></picture>](https://github.com/jin-jae) | 오수현&nbsp; [<picture><source media="(prefers-color-scheme: light)" srcset="./doc/image/github_dark.png" /><source media="(prefers-color-scheme: dark)" srcset="./doc/image/github_light.png" /><img src="./doc/image/github_dark.png" height="20" /></picture>](https://github.com/ocean010315) | 윤선웅&nbsp; [<picture><source media="(prefers-color-scheme: light)" srcset="./doc/image/github_dark.png" /><source media="(prefers-color-scheme: dark)" srcset="./doc/image/github_light.png" /><img src="./doc/image/github_dark.png" height="20" /></picture>](https://github.com/ssunbear) | 정민지&nbsp; [<picture><source media="(prefers-color-scheme: light)" srcset="./doc/image/github_dark.png" /><source media="(prefers-color-scheme: dark)" srcset="./doc/image/github_light.png" /><img src="./doc/image/github_dark.png" height="20" /></picture>](https://github.com/minjijeong98) 
|:-:|:-:|:-:|:-:|:-:|:-:|
| ![곽희준](https://avatars.githubusercontent.com/u/80732503) | ![김정은](https://avatars.githubusercontent.com/u/121777522) | ![김진재](https://avatars.githubusercontent.com/u/97018331) | ![오수현](https://avatars.githubusercontent.com/u/91974779) | ![윤선웅](https://avatars.githubusercontent.com/u/117508164) | ![정민지](https://avatars.githubusercontent.com/u/162319450) |

<br>

## 🧑🏻‍💻 역할 분담
| 팀원　　| 역할 |
|:--------:| -------------- |
| 곽희준 | 리뷰 요약 및 키워드 추출 - ASTE(파이프라인 설계, 데이터 엔지니어링, Metric 선정), Clustering을 통한 추천 키워드 포함 검색과 리뷰 요약 |
| 김정은 | 성분/영양 정보 추출 - YOLO11 SFT, CLOVA OCR output 후처리, Rule-based 방식 적용 실험, HCX Fine-Tuning, 평가 Metric 선정 |
| 김진재 | 크기 정보 묘사, 리뷰 요약 및 키워드 추출, 앱 개발 - 프로젝트 매니징, YOLO11 SFT, Rule-based 후처리, ASTE(HCX/DeepSeek Prompt Engineering, DeepSeek SFT), React Native, React (Chrome Extension) Spring Framework 개발 |
| 오수현 | 리뷰 요약 및 키워드 추출 - ASTE(HCX/DeepSeek Prompt Engineering, DeepSeek SFT), Clustering을 통한 추천 키워드 포함 검색과 리뷰 요약 |
| 윤선웅 | 대표 이미지 설명 생성 - Janus Pro Fine-Tuning, HCX 후처리(요약, 번역, Hallucination 제거), 1376개 대표 이미지 골드라벨 추출, VLM 평가 metric 설계 |
| 정민지 | 상품 설명 요약, 성분/영양 정보 추출 - 상품 설명 요약 HCX Fine-Tuning, 성분/영양 정보 평가 metric 설계 및 golden label 생성, OCR과 LLM을 활용한 성분/영양 정보 추출 로직 설계 및 실험 |

<br>

## 📅 프로젝트 타임라인

- 프로젝트 기간은 2025-01-10 ~ 2025-02-10입니다.

<img width="960" alt="image" src="https://github.com/user-attachments/assets/f75932a2-0cac-4fd2-8eb9-79d18849b49e" />

<br>

### 📁 프로젝트 구조

프로젝트 폴더 구조는 아래와 같습니다.

```
TBD
```

<br>

### 💾 프로젝트 설치 및 실행

TBD
