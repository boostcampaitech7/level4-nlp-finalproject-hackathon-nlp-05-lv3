from ultralytics import YOLO
import os
import torch
import cv2

# Load a trained model
model_path = "src/YOLO/yolo11n.pt"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file '{model_path}' not found.")

model = YOLO(model_path)

# Train the model
train_results = model.train(
    data="config/config.yaml",
    epochs=100,
    imgsz=640,
    device="cuda" if torch.cuda.is_available() else "cpu",
)

# Define the input and output directories
input_dir = "data/YOLO/inference/images"
output_dir = "data/YOLO/output/images"
labels_dir = "data/YOLO/output/labels"

# Ensure the output directories exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(labels_dir, exist_ok=True)

# Supported image extensions
image_extensions = (".png", ".jpg", ".jpeg")

# Process each image in the input directory
for img_name in os.listdir(input_dir):
    img_path = os.path.join(input_dir, img_name)
    
    # Check if it's an image file
    if not img_name.lower().endswith(image_extensions):
        continue
    
    # Perform object detection
    results = model(img_path)

    for result in results:
        # Check if any detection exists
        if result.boxes is None or len(result.boxes) == 0:
            continue

        # Load original image
        img = cv2.imread(img_path)

        # Draw detection results on the image
        plotted_img = result.plot()
        
        # Save the resulting image
        save_path = os.path.join(output_dir, img_name)
        cv2.imwrite(save_path, plotted_img)

        # Save label file (YOLO format: class x_center y_center width height)
        label_file = os.path.join(labels_dir, img_name.rsplit(".", 1)[0] + ".txt")
        with open(label_file, "w") as f:
            for box, cls in zip(result.boxes.xywhn, result.boxes.cls):
                x_center, y_center, width, height = box.tolist()
                class_id = int(cls.item())
                f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")  # YOLO 형식 저장
