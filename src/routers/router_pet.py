from fastapi import APIRouter, Depends, HTTPException, status
from src.database import DatabaseConnection
from src.modules.auth_handler import AuthHandler
from sqlalchemy.orm import Session

from src.modules.pet import CreatePet, GetPet, UpdatePet
from src.schemas.auth import UserDataToken
from src.schemas.basic_response import BasicResponse
from src.schemas.pet import GetPetResponse, PostPet, PutPet


router = APIRouter(prefix="/pets", tags=["Pets"])


@router.get("/")
def get_pets(
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[list[GetPetResponse]]:
    return GetPet(session).execute()  # type: ignore[return-value]


@router.get("/{id}")
def get_pet(
    id: int | None = None,
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[GetPetResponse]:
    return GetPet(session, id).execute()  # type: ignore[return-value]


@router.post("/")
def create_pet(
    request: PostPet,
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    return CreatePet(request=request, session=session).execute()


@router.put("/{id}")
def update_pet(
    id: int,
    request: PutPet,
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    return UpdatePet(session, request, id).execute()
