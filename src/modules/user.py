from enum import Enum
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from auth.auth_utils import Auth
from database.model import User
from schemas.basic_response import BasicResponse
from schemas.user import GetUserResponse, PostUser

class Operation(Enum):
    ONE_USER = "One user"
    ALL_USERS = "All users"

class GetUser:
    def __init__(self, session: Session, user_id: int | None):
        self._session = session
        self._user_id = user_id
        self._operation = Operation | None

    
    def _define_operation(self) -> None:
        self.operation = Operation.ONE_USER if self._user_id else Operation.ALL_USERS

    def execute(self) -> BasicResponse[list[GetUserResponse] | GetUserResponse]:
        data: list[GetUserResponse] | GetUserResponse
        try:
            self._define_operation()
            if self.operation == Operation.ALL_USERS:
                data = self._get_users()
            else:
                data = self._get_user()
            return BasicResponse(data=data)
        except Exception as e:
            raise HTTPException(
                detail=f"Erro interno: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    def _get_users(self) -> list[GetUserResponse]:
        with self._session as db:
            users = db.query(User).options(joinedload(User.pets)).all()
            serialized_users = [GetUserResponse.from_orm(user) for user in users]
            return serialized_users

    def _get_user(self) -> GetUserResponse:
        with self._session as db:
            user: User = (
                db.query(User).options(joinedload(User.agents)).get(self._user_id)  # type: ignore[assignment]
            )
            if not user:
                raise HTTPException(
                    detail="Usuário não existe", status_code=status.HTTP_404_NOT_FOUND
                )
            serialized_user = GetUserResponse.from_orm(user)
            return serialized_user
    
class CreateUser:
    def __init__(self, session: Session, request: PostUser):
        self.session = session
        self.request = request

    def execute(self) -> BasicResponse[None]:
        try:
            with self.session as session:
                self._create_user(session)
                session.commit()
                return BasicResponse(message="OK")
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao criar o usuário: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_user(self, session: Session) -> User | None:
        hashed_password = Auth.get_password_hash(self.request.password)
        user = User(
            name=self.request.name,
            email=self.request.email,
            password=hashed_password,
        )
        session.add(user)
        session.flush()
        session.refresh(user)
        return user

class UpdateUser():
    def execute(request: PostUser, session: Session):
        return