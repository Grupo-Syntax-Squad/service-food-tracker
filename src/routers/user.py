from fastapi import APIRouter, Depends
from src.database import DatabaseConnection
from src.modules.auth_handler import AuthHandler
from sqlalchemy.orm import Session

from src.schemas.auth import UserDataToken
from src.schemas.basic_response import BasicResponse
from src.schemas.pet import PostPet
from src.modules.user import UpdateUserPets


router = APIRouter(prefix="/users", tags=["Users"])

# @router.get("/")
# def get_users(
#     current_user: CurrentUser = Depends(Auth.get_current_user),
#     session: Session = Depends(get_db),
# ) -> BasicResponse[list]:
#     return GetUser(session).execute()

# @router.get("/{id}")
# def get_user(
#     id: int,
#     current_user: CurrentUser = Depends(Auth.get_current_user),
#     session: Session = Depends(get_db),
# ) -> BasicResponse[list]:
#     return GetUser(session, user_id=id).execute()

# @router.post("/")
# def create_user(
#     request: PostUser,
#     #current_user: CurrentUser = Depends(Auth.get_current_user),
#     session: Session = Depends(get_db),
# ) -> BasicResponse[None]:
#     return CreateUser(request=request, session=session)

# @router.put("/{id}")
# def update_user(
#     id: int,
#     request: PostUser,
#     current_user: CurrentUser = Depends(Auth.get_current_user),
#     session: Session = Depends(get_db),
# ) -> BasicResponse[None]:
#     return UpdateUser(id, request, session)


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