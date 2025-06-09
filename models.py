from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class DetectionRecord(BaseModel):
    id: int
    label: str
    confidence: float
    camera_ip: str
    timestamp: str