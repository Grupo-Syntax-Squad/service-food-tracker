from fastapi import APIRouter, Depends, HTTPException, status
from src.database import DatabaseConnection
from src.modules.auth_handler import AuthHandler
from src.modules.pet import UpdatePet
from src.schemas.auth import UserDataToken
from src.schemas.common import BasicResponse
from src.schemas.pet import PutPet
from sqlalchemy.orm import Session


router = APIRouter(prefix="/pets", tags=["Pet"])

@router.put("/{id}")
def update_pet(
    id: int,
    request: PutPet,
    current_user: UserDataToken = Depends(AuthHandler().get_current_user),
    session: Session = Depends(DatabaseConnection().get_db_session),
) -> BasicResponse[None]:
    return UpdatePet(session, request, id)