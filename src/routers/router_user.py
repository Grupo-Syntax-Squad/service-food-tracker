from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import DatabaseConnection
from src.modules.user import CreateUser, GetUsers
from src.schemas.common import BasicResponse
from src.schemas.user import RequestCreateUser, ResponseGetUsers


router = APIRouter(prefix="/users", tags=["User"])


@router.post("/")
def create_user(
    request: RequestCreateUser,
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    return CreateUser(session, request).execute()


@router.get("/")
def get_users(
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[list[ResponseGetUsers]]:
    return GetUsers(session).execute()
