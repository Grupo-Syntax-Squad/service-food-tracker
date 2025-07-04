from contextlib import asynccontextmanager
from typing import Any, AsyncIterator
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from src.database import DatabaseConnection
from src.database.model import Pet
from src.modules.lifespan import LifespanHandler
from src.modules.notificator import UserNotificator

# from src.modules.scheduler import start_scheduler
from src.schemas.basic_response import BasicResponse
from src.schemas.detection import Detection, DetectionRequest
from src.modules.json_handler import JSONHandler
from src.routers import router_scheduled_feeding, router_user, router_auth, router_pet


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    LifespanHandler().execute()
    yield None


app = FastAPI(lifespan=lifespan)
# start_scheduler()


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Food Tracker API",
        version="1.0.0",
        description="API for pets food tracking",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]


@app.get("/", include_in_schema=False)
def index() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.post("/detectar")
async def detectar(
    request: DetectionRequest,
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[Detection]:
    detection = Detection(timestamp=request.timestamp)
    JSONHandler(settings.json_file_path).save_in_json(detection)
    pet = session.execute(select(Pet).where(Pet.id == 1)).unique().scalar_one_or_none()
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pet não encontrado"
        )
    UserNotificator(session).notificate(pet)
    return BasicResponse(data=detection)


app.include_router(router_user.router)
app.include_router(router_auth.router)
app.include_router(router_scheduled_feeding.router)
app.include_router(router_pet.router)
