from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.auth_utils import Auth
from database import get_db
from modules.pet import CreatePet, GetPet
from schemas.auth import CurrentUser
from schemas.basic_response import BasicResponse
from schemas.pet import PostPet


router = APIRouter(prefix="/pets", tags=["Pets"])

@router.get("/")
def get_pets(
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[list]:
    return GetPet(session).execute()

@router.get("/{id}")
def get_pet(
    id: int,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[list]:
    return GetPet(session, id).execute()

@router.post("/")
def create_pet(
    request: PostPet,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    return CreatePet(request=request, session=session)

@router.put("/{id}")
def update_pet(
    id: int,
    request: PostPet,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    return UpdatePet(id, request, session)