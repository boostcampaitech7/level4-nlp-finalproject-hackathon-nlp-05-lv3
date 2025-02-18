import requests
from io import BytesIO
import pandas as pd
from PIL import Image

from ultralytics import YOLO


compare_actual_sizes = {
    1: {"name": "2L 페트병", "width_cm": 9.0, "height_cm": 31.0},
    2: {"name": "500ml 캔", "width_cm": 6.5, "height_cm": 16.5},
    3: {"name": "종이컵", "width_cm": 7.0, "height_cm": 7.5}
}


def download_image(url):
    response = requests.get(url)
    response.raise_for_status()  # 오류 발생 시 예외 처리
    return Image.open(BytesIO(response.content))


def get_detection_from_image(image_dir, model_path, show=False):
    model = YOLO(model_path)
    image = None
    
    if image_dir.startswith("https"):
        image = download_image(image_dir)
    else:
        image = Image.open(image_dir)
    results = model(image, conf=0.3)
    
    if show:
        # 결과 시각화 및 저장
        for idx, result in enumerate(results):
            result.show()

        # 감지된 객체 정보 출력
        for result in results:
            print("Bounding Boxes:", result.boxes.xyxy)
            print("Class IDs:", result.boxes.cls)
            print("Confidence Scores:", result.boxes.conf)

    return results


def process_result_with_actual_size_desc(result):
    boxes = result.boxes.xyxy
    classes = result.boxes.cls

    # product(0) 후보와 compare(1,2,3) 후보를 분리해서 저장
    product_candidates = []  # (box)
    compare_candidates = []  # (box, class_id)

    for box, cls_id in zip(boxes, classes):
        cls_id_int = int(cls_id.item())  # 클래스 ID를 정수로 변환
        if cls_id_int == 0:  # product
            product_candidates.append(box)
        elif cls_id_int in [1, 2, 3]:  # compare
            compare_candidates.append((box, cls_id_int))

    # 만약 product나 compare 후보가 하나도 없다면 예외 처리
    if not product_candidates:
        print("product(0) 클래스 바운딩 박스가 없습니다.")
        return
    if not compare_candidates:
        print("compare(1,2,3) 클래스 바운딩 박스가 없습니다.")
        return

    # product 중에서 x2(오른쪽) 좌표가 가장 큰 박스 하나 선택
    selected_product_box = max(product_candidates, key=lambda b: b[2].item())

    # compare(1,2,3) 중에서 x2(오른쪽) 좌표가 가장 큰 박스과 그 클래스 ID를 하나 선택
    selected_compare_box, selected_compare_class = max(compare_candidates, key=lambda x: x[0][2].item())

    global compare_actual_sizes

    compare_info = compare_actual_sizes.get(selected_compare_class)
    if not compare_info:
        print("알 수 없는 비교 대상 클래스입니다.")
        return

    compare_name = compare_info["name"]

    compare_actual_width = compare_info["width_cm"]
    compare_actual_height = compare_info["height_cm"]

    compare_pixel_width = selected_compare_box[2].item() - selected_compare_box[0].item()
    compare_pixel_height = selected_compare_box[3].item() - selected_compare_box[1].item()

    scale_width = compare_actual_width / compare_pixel_width
    scale_height = compare_actual_height / compare_pixel_height

    product_pixel_width = selected_product_box[2].item() - selected_product_box[0].item()
    product_pixel_height = selected_product_box[3].item() - selected_product_box[1].item()

    product_actual_width = product_pixel_width * scale_width
    product_actual_height = product_pixel_height * scale_height

    width_ratio = product_actual_width / compare_actual_width
    height_ratio = product_actual_height / compare_actual_height

    def describe_ratio_first(ratio, compare_name, dimension):
        ratio = round(ratio, 3)
        base_text = f"{compare_name} {dimension}"

        # 정수와 같은지 체크
        if float(int(ratio)) == float(ratio):
            if ratio == 1:
                return f"{base_text}와 같고"
            return f"{base_text}의 {int(ratio)}배이고"
        
        if ratio > 1.5:
            # 반올림 한후, 올림이면 크다, 내림이면 작다 표시
            rounded_ratio = round(ratio)
            if rounded_ratio > ratio: # 2.0 > 1.9
                return f"{base_text}의 {rounded_ratio}배보다 조금 작고"
            if rounded_ratio < ratio: # 2.0 < 2.2
                return f"{base_text}의 {rounded_ratio}배보다 조금 크고"
        if ratio > 1.0:
            return f"{base_text}보다 조금 크고"
        if 0.5 <= ratio < 1.0:
            return f"{base_text}보다 조금 작고"
        return f"{base_text}보다 반 이상 작고"

    def describe_ratio(ratio, compare_name, dimension):
        ratio = round(ratio, 3)
        base_text = f"{compare_name} {dimension}"

        # 정수와 같은지 체크
        if float(int(ratio)) == float(ratio):
            if ratio == 1:
                return f"{base_text}와 같습니다."
            return f"{base_text}의 {int(ratio)}배입니다."
        
        if ratio > 1.5:
            # 반올림 한후, 올림이면 크다, 내림이면 작다 표시
            rounded_ratio = round(ratio)
            if rounded_ratio > ratio: # 2.0 > 1.9
                return f"{base_text}의 {rounded_ratio}배보다 조금 작습니다."
            if rounded_ratio < ratio: # 2.0 < 2.2
                return f"{base_text}의 {rounded_ratio}배보다 조금 큽니다."
        if ratio > 1.0:
            return f"{base_text}보다 조금 큽니다."
        if 0.5 <= ratio < 1.0:
            return f"{base_text}보다 조금 작습니다."
        return f"{base_text}보다 반 이상 작습니다."

    width_description = describe_ratio_first(width_ratio, compare_name, "너비")
    height_description = describe_ratio(height_ratio, compare_name, "높이")

    description = (
        f"배송받는 제품의 실제 너비는 {int(product_actual_width)}cm 정도로 {width_description}, 실제 높이는 {int(product_actual_height)}cm 정도로 {height_description}"
    )

    return description


def process_row(row, model):
    detection_result = get_detection_from_image(row["크기 이미지 URL"], model)
    
    if detection_result:
        return process_result_with_actual_size_desc(detection_result)
    return "이미지 분석 실패"
    


if __name__ == "__main__":
    model = YOLO("/data/ephemeral/home/workspace/personal/size_info/ultralytics/runs/detect/train14/weights/best.pt")

    df = pd.read_csv("250201_image_comparison.csv")
    df["size_description"] = df.apply(lambda row: process_row(row, model), axis=1)

    df.to_csv("size_description_output.csv", index=False)
