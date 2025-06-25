from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import DatabaseConnection
from src.modules.auth_handler import AuthHandler
from src.modules.scheduled_feeding import CreateScheduledFeeding
from src.schemas.auth import UserDataToken
from src.schemas.basic_response import BasicResponse
from src.schemas.scheduled_feeding import RequestCreateScheduledFeeding


router = APIRouter(prefix="/scheduled_feeding", tags=["Scheduled feeding"])


@router.post("/")
def create_scheduled_feeding(
    user: Annotated[UserDataToken, Depends(AuthHandler().get_current_user)],
    request: RequestCreateScheduledFeeding,
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    return CreateScheduledFeeding(session, request).execute()
