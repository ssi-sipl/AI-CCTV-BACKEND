from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from detector import start_detection, stop_detection
from database import get_all_detections, get_detections_by_label
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend on any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Login model
class LoginRequest(BaseModel):
    username: str
    password: str

# ✅ Login route
@app.post("/login")
def login(data: LoginRequest):
    if data.username == "admin" and data.password == "password":
        return {"status": "success"}
    return JSONResponse(status_code=401, content={"status": "fail"})

# ✅ Start detection
@app.post("/start-detection")
def start(camera_ip: str):
    start_detection(camera_ip)
    return {"status": "started"}

# ✅ Stop detection
@app.post("/stop-detection")
def stop(camera_ip: str):
    stop_detection(camera_ip)
    return {"status": "stopped"}

# ✅ Get detections (with optional label + time filter)
@app.get("/detections")
def detections(label: str = None, recent_seconds: int = 60):
    cutoff_time = (datetime.now() - timedelta(seconds=recent_seconds)).strftime('%Y-%m-%d %H:%M:%S')
    if label:
        return get_detections_by_label(label, cutoff_time)
    return get_all_detections(cutoff_time)
