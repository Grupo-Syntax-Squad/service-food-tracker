from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import DatabaseConnection
from src.modules.auth_handler import AuthHandler
from src.modules.user import CreateUser, DeleteUser, GetUsers, UpdateUser
from src.schemas.auth import UserDataToken
from src.schemas.basic_response import BasicResponse
from src.schemas.user import RequestCreateUser, RequestUpdateUser, ResponseGetUsers


router = APIRouter(prefix="/users", tags=["User"])


@router.post("/")
def create_user(
    user: Annotated[UserDataToken, Depends(AuthHandler().get_current_user)],
    request: RequestCreateUser,
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    return CreateUser(session, request).execute()


@router.put("/")
def update_user(
    user: Annotated[UserDataToken, Depends(AuthHandler().get_current_user)],
    request: RequestUpdateUser,
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    return UpdateUser(session, request).execute()


@router.get("/")
def get_users(
    user: Annotated[UserDataToken, Depends(AuthHandler().get_current_user)],
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[list[ResponseGetUsers]]:
    return GetUsers(session).execute()


@router.delete("/")
def delete_user(
    user: Annotated[UserDataToken, Depends(AuthHandler().get_current_user)],
    user_id: int = Query(),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    return DeleteUser(session, user_id).execute()
