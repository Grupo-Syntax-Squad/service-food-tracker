import json
import os
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

DATA_FILE = "data.json"


class Detection(BaseModel):
    timestamp: str


def save_in_json(data: dict):
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = json.load(f)
        except json.JSONDecodeError:
            content = []
    else:
        content = []

    content.append(data)

    with open(DATA_FILE, "w") as f:
        json.dump(content, f, indent=4)


@app.post("/detectar")
async def detectar(detection: Detection):
    entry = {
        "timestamp": detection.timestamp,
        "received_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_in_json(entry)
    return {"status": "ok", "data": entry}


#  uvicorn main:app --reload --host 0.0.0.0 --port 8000
