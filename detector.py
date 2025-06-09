import threading
import time
import cv2
import torch
from database import insert_detection, clear_detections

running_detectors = {}
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)
CONFIDENCE_THRESHOLD = 0.7

def start_detection(camera_ip):
    def detect():
        cap = cv2.VideoCapture(camera_ip)
        if not cap.isOpened():
            print(f"[ERROR] Cannot open camera {camera_ip}")
            return

        while running_detectors.get(camera_ip, False):
            ret, frame = cap.read()
            if not ret or frame.mean() < 10:
                continue

            results = model(frame)

            for *box, conf, cls in results.xyxy[0]:
                if conf < CONFIDENCE_THRESHOLD:
                    continue
                label = model.names[int(cls)]
                print(f"[{camera_ip}] Detected {label} ({conf:.2f})")
                insert_detection(label, float(conf) * 100, camera_ip)

            time.sleep(0.5)

        cap.release()

    running_detectors[camera_ip] = True
    thread = threading.Thread(target=detect, daemon=True)
    thread.start()

def stop_detection(camera_ip):
    running_detectors[camera_ip] = False
    clear_detections(camera_ip)
