from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.auth_utils import Auth
from database import get_db
from schemas.auth import CurrentUser
from schemas.basic_response import BasicResponse


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def get_users(
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[list]:

    return GetUser(session).execute()