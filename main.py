from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from config import Settings
from src.schemas.common import BasicResponse
from src.schemas.detection import Detection, DetectionRequest
from src.modules.json_handler import JSONHandler

settings = Settings()
app = FastAPI()


@app.get("/", include_in_schema=False)
def index() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.post("/detectar")
async def detectar(request: DetectionRequest) -> BasicResponse[Detection]:
    detection = Detection(timestamp=request.timestamp)
    JSONHandler(settings.json_file_path).save_in_json(detection)
    return BasicResponse(data=detection)
