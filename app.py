from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from detector import start_detection, stop_detection
from database import get_all_detections, get_detections_by_label
from datetime import datetime, timedelta
import cv2

app = FastAPI()

# CORS to allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Login ----------

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginRequest):
    if data.username == "admin" and data.password == "password":
        return {"status": "success"}
    return JSONResponse(status_code=401, content={"status": "fail"})

# ---------- Start/Stop Detection ----------

@app.post("/start-detection")
def start(camera_ip: str):
    start_detection(camera_ip)
    return {"status": "started"}

@app.post("/stop-detection")
def stop(camera_ip: str):
    stop_detection(camera_ip)
    return {"status": "stopped"}

# ---------- Detections Endpoint ----------

@app.get("/detections")
def detections(label: str = None, recent_seconds: int = 60):
    cutoff_time = (datetime.now() - timedelta(seconds=recent_seconds)).strftime('%Y-%m-%d %H:%M:%S')
    if label:
        return get_detections_by_label(label, cutoff_time)
    return get_all_detections(cutoff_time)

# ---------- Stream RTSP to MJPEG (for <img> tag) ----------

@app.get("/stream")
def stream_rtsp(camera_url: str):
    def generate():
        cap = cv2.VideoCapture(camera_url)
        if not cap.isOpened():
            print(f"[ERROR] Cannot open stream: {camera_url}")
            return

        while True:
            success, frame = cap.read()
            if not success:
                continue

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
