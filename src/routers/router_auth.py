from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.modules.auth_handler import AuthHandler
from src.schemas.auth import Token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    return AuthHandler().login(form_data.username, form_data.password)
