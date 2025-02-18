# utils/common_utils.py

import os
import random
import numpy as np
import torch
import pandas as pd

def set_seed(seed: int = 42) -> None:
    """
    다양한 라이브러리와 플랫폼에서 재현성을 위한 시드 설정 함수.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_second_to_last(df: pd.DataFrame) -> pd.DataFrame:
    """
    각 그룹 내에서 'img-ID'를 기준으로 정렬한 후,
    각 그룹의 뒤에서 두 번째 행만 추출해 반환.
    """
    df = df.sort_values(
        by='img-ID',
        key=lambda s: s.str.split('-').str[-1].astype(int),
        ascending=True
    )
    return df.iloc[0]


def load_and_filter_data(csv_path: str) -> pd.DataFrame:
    """
    1. CSV 로드
    2. ID별 '전체' 행 정보를 '개별' 행에 채워넣기
    3. ID별 뒤에서 두 번째 행만 추출
    4. '?ref=storefarm' 제거
    5. 정렬 후 반환
    """
    # 1) CSV 로드
    df_raw = pd.read_csv(csv_path)
    df = df_raw.copy()

    # 2) '전체' 데이터 추출 후, '개별'에 정보 채워넣기
    df_total = df[df['전체/개별'] == '전체'].copy()
    fill_cols = ['row', 'img-ID', '카테고리', '상품명', '상품 상세 URL']
    info_dict = df_total.set_index('ID')[fill_cols].to_dict('index')
    for col in fill_cols:
        df[col] = df['ID'].map(lambda x: info_dict[x][col] if x in info_dict else None)

    # 3) 그룹별 뒤에서 두 번째 행 추출
    df_filtered = df.groupby('ID', group_keys=False).apply(get_second_to_last).reset_index(drop=True)

    # 4) 이미지 URL에서 '?ref=storefarm' 제거
    df_filtered['url_clean'] = df_filtered['이미지 URL'].str.replace('?ref=storefarm', '', regex=False)

    # 5) row 기준 정렬
    df_filtered = df_filtered.sort_values(by="row").reset_index(drop=True)

    return df_filtered