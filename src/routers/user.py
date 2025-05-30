from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.auth_utils import Auth
from database import get_db
from modules.user import CreateUser, GetUser, UpdateUser
from schemas.auth import CurrentUser
from schemas.basic_response import BasicResponse
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
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    return CreateUser(request=request, session=session)

def update_user(
    request: PostUser,
    current_user: CurrentUser = Depends(Auth.get_current_user),
    session: Session = Depends(get_db),
) -> BasicResponse[None]:
    return UpdateUser(request, session)