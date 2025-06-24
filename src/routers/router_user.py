from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import DatabaseConnection
from src.modules.auth_handler import AuthHandler
from src.modules.user import CreateUser, DeleteUser, GetUsers, UpdateUser, UpdateUserPets
from src.schemas.auth import UserDataToken
from src.schemas.basic_response import BasicResponse
from src.schemas.pet import PostPet
from src.schemas.user import RequestCreateUser, RequestUpdateUser, ResponseGetUser

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/")
def create_user(
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
) -> BasicResponse[list[ResponseGetUser]]:
    return GetUsers(session).execute()


@router.delete("/")
def delete_user(
    user: Annotated[UserDataToken, Depends(AuthHandler().get_current_user)],
    user_id: int = Query(),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    return DeleteUser(session, user_id).execute()


@router.post("/{id}/add_pet", response_model=BasicResponse[None])
def add_pet_to_user(
    id: int,
    request: PostPet,
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    service = UpdateUserPets(session, id)
    return service.add_pet(request)


@router.delete("/{id}/remove_pet/{pet_id}", response_model=BasicResponse[None])
def remove_pet_from_user(
    id: int,
    pet_id: int,
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    service = UpdateUserPets(session, id)
    return service.remove_pet(pet_id)
