from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.database.get_db import get_db
from src.database.model import User
from sqlalchemy.orm import Session
from src.auth.auth_utils import (
    Auth,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.schemas.auth import Token


class LoginForm(BaseModel):
    email: str
    password: str


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: LoginForm, db: Session = Depends(get_db)
) -> dict[str, str]:
    with db as session:
        user = session.query(User).filter(User.email == form_data.email).first()
        if user is None or not Auth.verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorretos"
            )
        session.commit()

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = Auth.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}
