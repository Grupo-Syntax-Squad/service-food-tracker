from datetime import time
from pydantic import BaseModel


class RequestCreateScheduledFeeding(BaseModel):
    pet_id: int
    feeding_time: time
