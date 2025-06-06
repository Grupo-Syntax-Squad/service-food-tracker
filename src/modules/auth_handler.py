import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from sqlalchemy import select
from passlib.context import CryptContext

from config import Settings
from src.database import DatabaseConnection
from src.database.model import User
from src.modules.log import Log
from src.schemas.auth import Token, UserDataToken

security = HTTPBearer()

settings = Settings()


class AuthHandler:
    def __init__(self) -> None:
        self._log = Log()
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def login(self, email: str, password: str) -> Token:
        try:
            session_generator = DatabaseConnection().get_db_session()
            self._session = next(session_generator)
            self._log.info("Trying to login")
            user = self._get_user_by_email(email)
            if not self._verify_password(password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Senha incorreta",
                )
            encoded_token = self._create_access_token(user)
            self._log.info("Login successfully")
            return Token(access_token=encoded_token, token_type="bearer")
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error login: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno"
            )
        finally:
            try:
                session_generator.close()
            except Exception as close_error:
                self._log.error("Error closing DB session: %s", str(close_error))

    def _get_user_by_email(self, email: str) -> User:
        result = self._session.execute(
            select(User).where(User.email == email, User.enabled)
        ).scalar_one_or_none()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
            )
        return result

    def _hash_password(self, password: str) -> str:
        return self._pwd_context.hash(password)

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return self._pwd_context.verify(password, hashed_password)

    def _create_access_token(self, user: User) -> str:
        token = UserDataToken(
            user_id=user.id,
            username=user.name,
            email=user.email,
            exp=datetime.now(timezone.utc)
            + timedelta(minutes=settings.access_token_expires_minutes),
        )
        encoded_token = self._encode_token(token)
        return encoded_token

    def _encode_token(self, token: UserDataToken) -> str:
        token_json = token.model_dump()
        return jwt.encode(token_json, settings.secret_key, algorithm=settings.algorithm)

    def get_current_user(
        self, credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
    ) -> UserDataToken:
        try:
            self._log.info("Trying to get token data")
            session_generator = DatabaseConnection().get_db_session()
            self._session = next(session_generator)
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

            encoded_token = credentials.credentials
            decoded_token = self._decode_token(encoded_token)
            token = self._build_token_from_decoded_token(decoded_token)
            _ = self._get_user_by_email(token.email)
            self._log.info("Get token data successfully")
            return token
        except ValidationError:
            raise credentials_exception
        except jwt.InvalidTokenError:
            raise credentials_exception
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error getting current user: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno"
            )
        finally:
            try:
                session_generator.close()
            except Exception as close_error:
                self._log.error("Error closing DB session: %s", str(close_error))

    def _decode_token(self, token: str) -> Any:
        return jwt.decode(token, settings.secret_key, settings.algorithm)

    def _build_token_from_decoded_token(
        self, decoded_token: dict[str, Any]
    ) -> UserDataToken:
        user_id = decoded_token.get("user_id", None)
        username = decoded_token.get("username", None)
        email = decoded_token.get("email", None)
        exp = decoded_token.get("exp", None)
        return UserDataToken(user_id=user_id, username=username, email=email, exp=exp)
