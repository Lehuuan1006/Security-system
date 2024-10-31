import cv2
import torch
from ultralytics import YOLO
import requests
import numpy as np

# Tải mô hình YOLOv5 (sử dụng model pre-trained)
model = YOLO('yolov5s.pt')

# ESP32-CAM IP address
esp32cam_url = 'http://192.168.1.149:81/stream'  # Đặt URL của ESP32-CAM

def get_esp32cam_image():
    stream = requests.get(esp32cam_url, stream=True)
    if stream.status_code != 200:
        print("Error: Could not open video stream")
        return None

    bytes = b''
    for chunk in stream.iter_content(chunk_size=1024):
        bytes += chunk
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')

        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            return img

    return None

# Main loop
while True:
    # Capture an image from ESP32-CAM
    frame = get_esp32cam_image()
    if frame is None:
        break

    # Sử dụng YOLOv5 để dự đoán
    results = model(frame)

    # Lấy các đối tượng dự đoán
    detected_people = [r for r in results[0].boxes if r.cls[0] == 0]  # Lớp '0' là người trong COCO dataset

    # Vẽ khung giới hạn xung quanh các đối tượng người
    if len(detected_people) > 0:
        for person in detected_people:
            box = person.xyxy[0].cpu().numpy().astype(int)
            x_min, y_min, x_max, y_max = box
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        
        # Hiển thị cảnh báo "Có chuyển động"
        cv2.putText(frame, 'Co nguoi', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    else:
        # Hiển thị trạng thái "Secure"
        cv2.putText(frame, 'Secure', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)


    # Hiển thị ảnh
    cv2.imshow('Person Detection', frame)

    # Thoát bằng cách nhấn 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
