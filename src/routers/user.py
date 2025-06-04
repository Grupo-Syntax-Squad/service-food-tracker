from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.auth_utils import Auth
from database import get_db
from modules.user import CreateUser, GetUser, UpdateUser, UpdateUserPets
from schemas.auth import CurrentUser
from schemas.basic_response import BasicResponse
from schemas.pet import PostPet
from schemas.user import PostUser


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def get_users(
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[list]:
    return GetUser(session).execute()

@router.get("/{id}")
def get_user(
    id: int,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[list]:
    return GetUser(session, user_id=id).execute()

@router.post("/")
def create_user(
    request: PostUser,
    #current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    return CreateUser(request=request, session=session)

@router.put("/{id}")
def update_user(
    id: int,
    request: PostUser,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    return UpdateUser(id, request, session)

router.post("/{id}/add_pet", response_model=BasicResponse[None])
def add_pet_to_user(
    id: int,
    request: PostPet,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    service = UpdateUserPets(session, id)
    return service.add_pet(request)

@router.delete("/{id}/remove_pet/{pet_id}", response_model=BasicResponse[None])
def remove_pet_from_user(
    id: int,
    pet_id: int,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    service = UpdateUserPets(session, id)
    return service.remove_pet(pet_id)