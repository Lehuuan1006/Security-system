import cv2
import torch
from ultralytics import YOLO

# Tải mô hình YOLOv5 (sử dụng model pre-trained)
model = YOLO('yolov5s.pt')  # Bạn có thể thay thế bằng 'yolov5m.pt' hoặc 'yolov5l.pt' nếu muốn

# Khởi tạo camera
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
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
        cv2.putText(frame, 'Co chuyen dong', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    else:
        # Hiển thị trạng thái "Secure"
        cv2.putText(frame, 'Secure', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    # Thêm chữ "Hữu Ấn - Việt Bình" ở góc dưới cùng bên phải
    text = 'Huu An - Viet Binh'
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = frame.shape[1] - text_size[0] - 10
    text_y = frame.shape[0] - 10
    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    # Hiển thị ảnh
    cv2.imshow('Person Detection', frame)

    # Thoát bằng cách nhấn 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
