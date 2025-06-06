from fastapi import APIRouter

from src.modules.auth_handler import AuthHandler
from src.schemas.auth import RequestLogin, Token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(
    request: RequestLogin,
) -> Token:
    return AuthHandler().login(request.email, request.password)
