import pandas as pd
import Levenshtein

def compare_ingredient_files(file1, file2):
    # CSV 파일 로드
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # 필요한 컬럼 선택
    columns_to_compare = ['원재료', '알레르기(1차)', '알레르기(2차)', '보관방법(개봉전)', '보관방법(개봉후)']
    df1 = df1[['img-ID'] + columns_to_compare]
    df2 = df2[['img-ID'] + columns_to_compare]
    
    # img-ID 기준으로 병합
    merged_df = pd.merge(df1, df2, on='img-ID', suffixes=('_50', '_323'))
    
    # NaN 값을 빈 문자열로 변환 후 공백 제거
    for col in columns_to_compare:
        merged_df[f'{col}_50'] = merged_df[f'{col}_50'].fillna('').astype(str).str.replace(" ", "", regex=True)
        merged_df[f'{col}_323'] = merged_df[f'{col}_323'].fillna('').astype(str).str.replace(" ", "", regex=True)
    
    # Levenshtein 거리 및 유사도 계산
    for col in columns_to_compare:
        merged_df[f'Levenshtein_Distance_{col}'] = merged_df.apply(
            lambda row: Levenshtein.distance(row[f'{col}_50'], row[f'{col}_323']), axis=1
        )
        
        merged_df[f'Similarity_Ratio_{col}'] = merged_df.apply(
            lambda row: Levenshtein.ratio(row[f'{col}_50'], row[f'{col}_323']), axis=1
        )
    
    # 평균 유사도 계산
    avg_similarities = {
        col: merged_df[f'Similarity_Ratio_{col}'].mean() for col in columns_to_compare
    }
    
    # 결과 출력
    print(f'총 비교된 항목 수: {len(merged_df)}')
    for col in columns_to_compare:
        print(f'평균 유사도 ({col}): {avg_similarities[col] * 100:.2f}%')
    
    return merged_df

# 사용 예시
file1 = 'data/HCX/eval/images_50_ingredient_processed.csv'
file2 = 'data/HCX/inference/images_323_ingredient.csv'
result_df = compare_ingredient_files(file1, file2)
