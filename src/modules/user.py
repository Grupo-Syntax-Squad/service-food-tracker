from enum import Enum
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from auth.auth_utils import Auth
from database.model import Pet, User
from schemas.basic_response import BasicResponse
from schemas.pet import PostPet
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
                db.query(User).options(joinedload(User.pets)).get(self._user_id)  # type: ignore[assignment]
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
    def __init__(self, id: int, session: Session, request: PostUser):
        self._user_id = id
        self._session = session
        self._request = request

    def execute(self):
        try:
            self._get_user()
            self._update_user()  
            self._session.commit()      
            return BasicResponse()
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                detail=f"Erro interno: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def _get_user(self) -> None:
        query = select(User).where(User.id == self._user_id)
        result = self._session.execute(query)
        self._user = result.unique().scalar_one_or_none()
        if self._user is None:
            raise HTTPException(
                detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND
            )
        
    def _update_user(self):
        if self._request.name:
            self._user.name = self._request.name
        if self._request.email:
            self._user.name = self._request.email
        if self._request.password:
            self._user.name = self._request.password
        self._session.add(self._user)

class UpdateUserPets:
    def __init__(self, session: Session, user_id: int):
        self._session = session
        self._user_id = user_id
        self._user: User | None = None

    def _load_user(self) -> None:
        self._user = self._session.get(User, self._user_id)
        if not self._user:
            raise HTTPException(
                detail="Usuário não encontrado",
                status_code=status.HTTP_404_NOT_FOUND
            )

    def add_pet(self, pet_data: PostPet) -> BasicResponse:
        try:
            self._load_user()
            pet = Pet(
                name=pet_data.name,
                breed=pet_data.breed,
                castred=pet_data.castred,
                weight=pet_data.weight,
                color=pet_data.color,
                kind=pet_data.kind,
                user_id=self._user.id
            )
            self._session.add(pet)
            self._session.commit()
            return BasicResponse(message="Pet adicionado com sucesso.")
        except Exception as e:
            self._session.rollback()
            raise HTTPException(
                detail=f"Erro ao adicionar pet: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def remove_pet(self, pet_id: int) -> BasicResponse:
        try:
            self._load_user()
            pet = self._session.get(Pet, pet_id)
            if not pet or pet.user_id != self._user_id:
                raise HTTPException(
                    detail="Pet não encontrado ou não pertence ao usuário.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            self._session.delete(pet)
            self._session.commit()
            return BasicResponse(message="Pet removido com sucesso.")
        except HTTPException:
            raise
        except Exception as e:
            self._session.rollback()
            raise HTTPException(
                detail=f"Erro ao remover pet: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )