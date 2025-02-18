import requests
from ultralytics import YOLO
from PIL import Image
from io import BytesIO


def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def train_yolo():
    # YOLO 모델 학습
    model = YOLO("yolo11m.pt")
    model.train(data="size_info.yaml", epochs=12)

    results = model.val()
    success = model.export(format="onnx")

if __name__ == "__main__":
    train_yolo()