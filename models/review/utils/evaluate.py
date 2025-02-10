import json
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm
from ast import literal_eval
from bert_score import score
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import confusion_matrix, classification_report


"""
사용 예시:
sys.path.append(os.path.abspath('../src'))
from evaluate import evaluate_aste

evaluate_aste(
    df, 
    golden_label_col="aste_golden_label", 
    model_prediction_col="aste_hcx", 
    # eval_threshold=0.85
)
"""



# 한글 폰트 설정 (Ubuntu에서는 'NanumGothic' 사용)
plt.rc('font', family='NanumGothic')
# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# def extract_triplets(json_str):
#     """
#     JSON 포맷 문자열을 파싱하여 triplet 리스트 반환.
#     각 triplet은 {"속성": ..., "평가": ..., "감정": ...} 형식임.
#     """
#     try:
#         triplets = json.loads(json_str)
#         return triplets
#     except Exception as e:
#         print("JSON 파싱 에러:", e)
#         print(json_str)
#         return []


def extract_triplets(json_str):
    """
    JSON 포맷 문자열을 파싱하여 triplet 리스트 반환.
    각 triplet은 {"속성": ..., "평가": ..., "감정": ...} 형식임.
    만약 "속성", "평가", "감정" 키가 없으면 각각 빈 문자열("")을 넣음.
    """
    try:
        triplets = literal_eval(json_str)
        
        # 각 triplet에 대해 키가 없으면 빈 문자열("")을 넣음
        for triplet in triplets:
            triplet["속성"] = triplet.get("속성", "")
            triplet["평가"] = triplet.get("평가", "")
            triplet["감정"] = triplet.get("감정", "")
        
        return triplets
    except Exception as e:
        print("JSON 파싱 에러:", e)
        print(json_str)
        return []
    

def bertscore_similarity(text1, text2):
    """
    BERTScore를 사용하여 두 문장의 유사도를 측정함.
    F1-score를 반환 (0~1).
    """
    P, R, F1 = score([text1], [text2], lang="ko", verbose=False, device="cuda")
    return F1.item()


def match_triplets(gl_triplets, hcx_triplets, eval_threshold=0.85):
    """
    GL와 HCX의 triplet 리스트 간에 '평가' 항목의 BERTScore 유사도를 기준으로
    1:1 매칭을 수행한다. Hungarian Algorithm을 활용하며, 유사도가 eval_threshold 이상인 경우만 후보로 선정한다.
    
    반환: [(gl_index, hcx_index, similarity), ...] (similarity >= eval_threshold)
    """
    if len(gl_triplets) == 0 or len(hcx_triplets) == 0:
        return []  # 매칭 불가
    
    num_gl = len(gl_triplets)
    num_hcx = len(hcx_triplets)
    cost_matrix = np.zeros((num_gl, num_hcx))
    sim_matrix = np.zeros((num_gl, num_hcx))
    
    # 각 pair에 대해 '평가' 항목의 유사도를 계산하여 cost matrix 구성
    for i, gl in enumerate(gl_triplets):
        for j, hcx in enumerate(hcx_triplets):
            sim = bertscore_similarity(gl["평가"], hcx["평가"])
            sim_matrix[i, j] = sim
            cost_matrix[i, j] = 1 - sim  # cost: 유사도가 높으면 낮은 cost
    
    # Hungarian Algorithm 적용
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    candidate_matches = []
    for i, j in zip(row_ind, col_ind):
        sim = sim_matrix[i, j]
        if sim >= eval_threshold:
            candidate_matches.append((i, j, sim))
    return candidate_matches


def evaluate_instance(gl_triplets, hcx_triplets, eval_threshold=0.85):
    """
    한 인스턴스(하나의 원문)에 대해 GL와 HCX triplet 세트를 평가한다.
    
    1. Hungarian Algorithm을 통해 '평가' 항목 기반 1:1 매칭을 수행한다.
    2. 매칭된 각 triplet 후보에 대해:
       - '평가': 유사도가 eval_threshold 이상이므로 TP로 간주.
       - '속성'과 '감정': GL와 HCX 값이 정확히 일치하면 TP, 불일치하면 오류로 간주하여
         라벨 측면에서 FN, 예측 측면에서 FP로 기록.
    3. 매칭되지 않은 triplet에 대해서는:
       - 라벨에만 있으면 FN (세 항목 모두)
       - 예측에만 있으면 FP (세 항목 모두)
    
    반환: {'속성': {"TP": ..., "FN": ..., "FP": ...}, 
          '평가': {"TP": ..., "FN": ..., "FP": ...}, 
          '감정': {"TP": ..., "FN": ..., "FP": ...}}
    """
    # 초기화
    counts = {
        "속성": {"TP": 0, "FN": 0, "FP": 0},
        "평가": {"TP": 0, "FN": 0, "FP": 0},
        "감정": {"TP": 0, "FN": 0, "FP": 0}
    }
    
    # 1:1 매칭 (평가 항목 기준)
    candidate_matches = match_triplets(gl_triplets, hcx_triplets, eval_threshold)
    matched_gl_indices = set()
    matched_hcx_indices = set()
    
        # 매칭된 후보들에 대해 세부 평가
    for i, j, sim in candidate_matches:
        matched_gl_indices.add(i)
        matched_hcx_indices.add(j)
        
        # '평가' 항목은 유사도 eval_threshold 이상이므로 TP로 기록
        counts["평가"]["TP"] += 1
        
        # '속성' 평가: 일치하면 TP, 불일치면 오류로 FN(라벨) 및 FP(예측) 처리
        if gl_triplets[i]["속성"] == hcx_triplets[j]["속성"]:
            counts["속성"]["TP"] += 1
        else:
            counts["속성"]["FN"] += 1
            counts["속성"]["FP"] += 1
        
        # '감정' 평가: 일치하면 TP, 불일치면 오류로 FN 및 FP 처리
        if gl_triplets[i]["감정"] == hcx_triplets[j]["감정"]:
            counts["감정"]["TP"] += 1
        else:
            counts["감정"]["FN"] += 1
            counts["감정"]["FP"] += 1

    # 매칭되지 않은 triplet 처리
    # 라벨에만 있는 triplet: FN (세 항목 모두)
    for idx in range(len(gl_triplets)):
        if idx not in matched_gl_indices:
            counts["속성"]["FN"] += 1
            counts["평가"]["FN"] += 1
            counts["감정"]["FN"] += 1
    # 예측에만 있는 triplet: FP (세 항목 모두)
    for idx in range(len(hcx_triplets)):
        if idx not in matched_hcx_indices:
            counts["속성"]["FP"] += 1
            counts["평가"]["FP"] += 1
            counts["감정"]["FP"] += 1
    
    return counts


def aggregate_evaluation(df, golden_label_col, model_prediction_col, eval_threshold=0.85):
    """
    데이터프레임(df)의 각 인스턴스에 대해 GL와 HCX triplet 세트를 평가하고,
    전체 TP, FN, FP를 집계하여 '속성', '평가', '감정' 각각에 대해 Precision, Recall, F1을 계산한다.
    
    동시에 속성(Aspect)과 감정(Sentiment)의 gold/pred 라벨을 수집하는데,
    단순히 1:1 매칭된 경우뿐 아니라, 매칭되지 않은 triplet에 대해
      - GL에만 존재하면 predicted는 "NO_PRED"로,
      - 예측에만 존재하면 gold는 "NO_GOLD"로 기록하여 전체 평가에 반영한다.
    
    또한, '평가' 항목의 BERTScore 유사도 리스트도 축적한다.
    
    반환:
      - metrics: 속성, 평가, 감정에 대한 Precision, Recall, F1-score 및 TP, FN, FP 개수
      - classification_data: [aspects_gold, aspects_pred, sentiments_gold, sentiments_pred] (전체 사례)
      - eval_similarities: 평가(BERTScore) 유사도 리스트 (매칭된 경우만)
    """
    total_counts = {
        "속성": {"TP": 0, "FN": 0, "FP": 0},
        "평가": {"TP": 0, "FN": 0, "FP": 0},
        "감정": {"TP": 0, "FN": 0, "FP": 0}
    }
    
    # 전체 classification 데이터를 위한 리스트 (매칭된 경우와 미매칭 사례 포함)
    aspects_gold_all = []
    aspects_pred_all = []
    sentiments_gold_all = []
    sentiments_pred_all = []
    eval_similarities = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        gl_triplets = extract_triplets(row[golden_label_col])
        hcx_triplets = extract_triplets(row[model_prediction_col])
        
        candidate_matches = match_triplets(gl_triplets, hcx_triplets, eval_threshold)
        matched_gl_indices = set([i for i, j, sim in candidate_matches])
        matched_hcx_indices = set([j for i, j, sim in candidate_matches])
        
        # 매칭된 경우: 실제 라벨을 기록
        for i, j, sim in candidate_matches:
            aspects_gold_all.append(gl_triplets[i]["속성"])
            aspects_pred_all.append(hcx_triplets[j]["속성"])
            sentiments_gold_all.append(gl_triplets[i]["감정"])
            sentiments_pred_all.append(hcx_triplets[j]["감정"])
            eval_similarities.append(sim)
            
        # 매칭되지 않은 GL triplet: 예측이 없으므로 predicted를 "NO_PRED"로 기록
        for idx_gl, gl_triplet in enumerate(gl_triplets):
            if idx_gl not in matched_gl_indices:
                aspects_gold_all.append(gl_triplet["속성"])
                aspects_pred_all.append("NO_PRED")
                sentiments_gold_all.append(gl_triplet["감정"])
                sentiments_pred_all.append("NO_PRED")
        
        # 매칭되지 않은 예측 triplet: GL에 해당하는 항목이 없으므로 gold를 "NO_GOLD"로 기록
        for idx_hcx, hcx_triplet in enumerate(hcx_triplets):
            if idx_hcx not in matched_hcx_indices:
                aspects_gold_all.append("NO_GOLD")
                aspects_pred_all.append(hcx_triplet["속성"])
                sentiments_gold_all.append("NO_GOLD")
                sentiments_pred_all.append(hcx_triplet["감정"])
        
        # 인스턴스별 평가 (전체 TP/FN/FP 집계)
        counts = evaluate_instance(gl_triplets, hcx_triplets, eval_threshold)
        for field in total_counts:
            total_counts[field]["TP"] += counts[field]["TP"]
            total_counts[field]["FN"] += counts[field]["FN"]
            total_counts[field]["FP"] += counts[field]["FP"]
    
    # 각 필드별 Precision, Recall, F1 계산
    metrics = {}
    for field, vals in total_counts.items():
        TP = vals["TP"]
        FN = vals["FN"]
        FP = vals["FP"]
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
        metrics[field] = {
            "Precision": precision,
            "Recall": recall,
            "F1": f1,
            "TP": TP,
            "FN": FN,
            "FP": FP
        }
    
    # 결과 출력
    print("최종 평가 결과:")
    for field, m in metrics.items():
        print(f"{field} -> Precision: {m['Precision']:.4f}, Recall: {m['Recall']:.4f}, F1: {m['F1']:.4f} (TP: {m['TP']}, FN: {m['FN']}, FP: {m['FP']})")
    
    classification_data = [aspects_gold_all, aspects_pred_all, sentiments_gold_all, sentiments_pred_all]
    return metrics, classification_data, eval_similarities


def extract_unique_labels(df, golden_label_col, model_prediction_col, field):
    """
    데이터프레임(df)에서 속성(Aspect) 및 감정(Sentiment)의 유니크한 값들을 추출하는 함수
    """
    labels = set()
    
    for _, row in df.iterrows():
        gl_triplets = extract_triplets(row[golden_label_col])
        hcx_triplets = extract_triplets(row[model_prediction_col])
        for triplet in gl_triplets + hcx_triplets:
            labels.add(triplet[field])
    
    # "NO_PRED"와 "NO_GOLD"도 결과에 포함
    labels.update(["NO_PRED", "NO_GOLD"])
    return sorted(list(labels))


def plot_confusion_matrix(y_true, y_pred, labels, title="Confusion Matrix"):
    """
    Confusion Matrix를 시각적으로 표시하는 함수
    """
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    df_cm = pd.DataFrame(cm, index=labels, columns=labels)
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(df_cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title(title)
    plt.show()


def plot_evaluation_similarity(eval_similarities):
    """
    '평가' 항목의 BERTScore 유사도 값을 히스토그램으로 시각화하는 함수
    """
    if not eval_similarities:
        print("평가 유사도 데이터가 없습니다.")
        return
    
    avg_similarity = np.mean(eval_similarities)
    median_similarity = np.median(eval_similarities)
    std_similarity = np.std(eval_similarities)

    plt.figure(figsize=(6, 5))
    sns.histplot(eval_similarities, bins=20, kde=True, color='blue')
    plt.axvline(avg_similarity, color='red', linestyle='dashed', linewidth=2, label=f'평균: {avg_similarity:.4f}')
    plt.axvline(median_similarity, color='green', linestyle='dashed', linewidth=2, label=f'중앙값: {median_similarity:.4f}')
    plt.xlabel("BERTScore Similarity")
    plt.ylabel("Frequency")
    plt.title("Evaluation BERTScore Similarity Distribution")
    plt.legend()
    plt.show()


def compute_confusion_and_report(df, golden_label_col, model_prediction_col, classification_data):
    """
    축적된 gold와 predicted 라벨을 이용하여, 속성과 감정에 대한 Confusion Matrix와
    Classification Report를 출력한다.
    """
    aspects_gold, aspects_pred, sentiments_gold, sentiments_pred = classification_data
    
    print("=== 속성 (Aspect) Confusion Matrix ===")
    aspect_labels = extract_unique_labels(df, golden_label_col, model_prediction_col, "속성")
    plot_confusion_matrix(aspects_gold, aspects_pred, labels=aspect_labels, title="Aspect Confusion Matrix")
    
    print("\n=== 속성 (Aspect) Classification Report ===")
    print(classification_report(aspects_gold, aspects_pred))
    
    print("=== 감정 (Sentiment) Confusion Matrix ===")
    sentiment_labels = extract_unique_labels(df, golden_label_col, model_prediction_col, "감정")
    plot_confusion_matrix(sentiments_gold, sentiments_pred, labels=sentiment_labels, title="Sentiment Confusion Matrix")
    
    print("\n=== 감정 (Sentiment) Classification Report ===")
    print(classification_report(sentiments_gold, sentiments_pred))


def compute_eval_statistics(eval_similarities):
    """
    '평가' 항목의 BERTScore 유사도 값에 대해 평균, 중앙값, 분포 등 통계를 출력한다.
    """
    if not eval_similarities:
        print("평가 유사도 데이터가 없습니다.")
        return None
    avg_similarity = np.mean(eval_similarities)
    median_similarity = np.median(eval_similarities)
    std_similarity = np.std(eval_similarities)
    
    plot_evaluation_similarity(eval_similarities)

    print("=== 평가 (Evaluation) 유사도 통계 ===")
    print(f"평균 유사도: {avg_similarity:.4f}")
    print(f"중앙값 유사도: {median_similarity:.4f}")
    print(f"표준편차: {std_similarity:.4f}")
    
    return avg_similarity, median_similarity, std_similarity


def evaluate_aste(df, golden_label_col, model_prediction_col, eval_threshold=0.85):
    """
    전체 평가 과정을 한 번에 실행하는 Wrapper 함수.

    1. aggregate_evaluation() 실행하여 성능 메트릭, Confusion Matrix용 데이터, 유사도 리스트 계산
    2. compute_confusion_and_report() 실행하여 Confusion Matrix 및 Classification Report 출력
    3. compute_eval_statistics() 실행하여 BERTScore 유사도 통계 출력

    Args:
        df (pd.DataFrame): 평가할 데이터프레임
        golden_label_col (str): 골든 라벨 컬럼명
        model_prediction_col (str): 모델 예측 컬럼명
        eval_threshold (float): BERTScore 유사도 기준 임계값

    Returns:
        dict: 전체 평가 메트릭 (metrics)
        list: Confusion Matrix 계산을 위한 classification_data ([aspects_gold, aspects_pred, sentiments_gold, sentiments_pred])
        list: 평가(BERTScore) 유사도 리스트 (eval_similarities)
    """
    print("\n=== Step 1: Aggregate Evaluation ===")
    metrics, classification_data, eval_similarities = aggregate_evaluation(
        df, 
        golden_label_col=golden_label_col, 
        model_prediction_col=model_prediction_col, 
        eval_threshold=eval_threshold
    )

    print("\n=== Step 2: Compute Confusion Matrix and Classification Report ===")
    compute_confusion_and_report(
        df=df, 
        golden_label_col=golden_label_col, 
        model_prediction_col=model_prediction_col,
        classification_data=classification_data
    )

    print("\n=== Step 3: Compute Evaluation Statistics (BERTScore Similarity) ===")
    compute_eval_statistics(eval_similarities)
