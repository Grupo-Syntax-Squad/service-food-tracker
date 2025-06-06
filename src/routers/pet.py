from fastapi import APIRouter, Depends, HTTPException, status
from src.database import DatabaseConnection
from src.modules.auth_handler import AuthHandler
from sqlalchemy.orm import Session

from src.modules.pet import CreatePet, GetPet
from src.schemas.auth import UserDataToken
from src.schemas.basic_response import BasicResponse
from src.schemas.pet import GetPetResponse, PostPet


router = APIRouter(prefix="/pets", tags=["Pets"])


@router.get("/")
def get_pets(
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[list[GetPetResponse]]:
    response = GetPet(session).execute()
    if type(response) is BasicResponse[list[GetPetResponse]]:
        return response
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno"
    )


@router.get("/{id}")
def get_pet(
    id: int | None = None,
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[GetPetResponse]:
    response = GetPet(session, id).execute()
    if type(response) is BasicResponse[GetPetResponse]:
        return response
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno"
    )


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
    request: PostPet,
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    raise HTTPException(
        status_code=status.HTTP_425_TOO_EARLY, detail="Em desenvolvimento"
    )
