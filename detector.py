import threading
import time
import cv2
import torch
from database import insert_detection, clear_detections

# Tracks which detectors are running
running_detectors = {}

# Load YOLOv5s model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)
CONFIDENCE_THRESHOLD = 0.7

# Optional mapping from camera IPs to full RTSP URLs
CAMERA_RTSP_MAP = {
    "192.168.1.73": "rtsp://admin:123456Ai@192.168.1.73:554/snl/live/1/3",
    "192.168.1.101": "rtsp://admin:123456Ai@192.168.1.101:554/snl/live/1/3",
    "192.168.1.102": "rtsp://admin:123456Ai@192.168.1.102:554/snl/live/1/3",
    "192.168.1.103": "rtsp://admin:123456Ai@192.168.1.103:554/snl/live/1/3",
}

def start_detection(camera_ip_or_rtsp):
    # Check if it's an IP, map to RTSP if possible
    rtsp_url = CAMERA_RTSP_MAP.get(camera_ip_or_rtsp, camera_ip_or_rtsp)

    def detect():
        print(f"[INFO] Starting detection on {rtsp_url}")
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            print(f"[ERROR] Cannot open camera stream: {rtsp_url}")
            return

        while running_detectors.get(camera_ip_or_rtsp, False):
            ret, frame = cap.read()
            if not ret or frame is None or frame.mean() < 10:
                print(f"[WARNING] Invalid or dark frame from {rtsp_url}")
                continue

            results = model(frame)

            for *box, conf, cls in results.xyxy[0]:
                if conf < CONFIDENCE_THRESHOLD:
                    continue
                label = model.names[int(cls)]
                print(f"[{camera_ip_or_rtsp}] Detected {label} ({conf:.2f})")
                insert_detection(label, float(conf) * 100, camera_ip_or_rtsp)

            time.sleep(0.5)

        cap.release()
        print(f"[INFO] Stopped detection on {rtsp_url}")

    running_detectors[camera_ip_or_rtsp] = True
    thread = threading.Thread(target=detect, daemon=True)
    thread.start()

def stop_detection(camera_ip_or_rtsp):
    print(f"[INFO] Stopping detection on {camera_ip_or_rtsp}")
    running_detectors[camera_ip_or_rtsp] = False
    #clear_detections(camera_ip_or_rtsp)
