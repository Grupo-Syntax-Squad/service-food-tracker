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


# (.venv) gabriel@pop-os:~/Github/sensorPresença$ uvicorn main:app --reload --host 0.0.0.0 --port 8000

import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.database.get_db import engine
from src.database.models import Base
from src.middlewares.logging import log_requests
from src.routers import (
    agent,
    auth,
    chat,
    example,
    group,
    knowledge_base,
    router_user,
    statistics,
    websocket_chat,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/", include_in_schema=False)
def index() -> RedirectResponse:
    return RedirectResponse("/docs")


app.middleware("http")(log_requests)
app.include_router(example.router)
app.include_router(router_user.router)
app.include_router(auth.router)
app.include_router(group.router)
app.include_router(agent.router)
app.include_router(websocket_chat.router)
app.include_router(chat.router)
app.include_router(knowledge_base.router)
app.include_router(statistics.router)
