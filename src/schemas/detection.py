from datetime import datetime

from pydantic import BaseModel


class DetectionRequest(BaseModel):
    timestamp: datetime


class Detection(BaseModel):
    timestamp: datetime
    received_at: datetime = datetime.now()
