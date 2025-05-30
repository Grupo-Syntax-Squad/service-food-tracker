from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Any
from passlib.context import CryptContext
from src.database.model import User
from src.database.get_db import get_db
from src.schemas.auth import CurrentUser
from src.settings import Settings

settings = Settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
NO_AUTH = settings.NO_AUTH

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Auth:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict[str, Any],
        expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def get_authorization_header(authorization: str = Header(None)) -> str | None:
        if NO_AUTH:
            return None
        if authorization is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is missing",
            )
        token = authorization.split(" ")[1] if " " in authorization else authorization
        return token

    @staticmethod
    def get_current_user(
        token: str = Depends(get_authorization_header), db: Session = Depends(get_db)
    ) -> CurrentUser | None:
        if NO_AUTH:
            return None
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = int(payload.get("sub", 0))
            if user_id is None:
                raise credentials_exception
            with db as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user is None or not user.enabled:
                    raise credentials_exception
        except JWTError:
            raise credentials_exception
        return CurrentUser.model_validate(user)
