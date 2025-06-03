from enum import Enum
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from auth.auth_utils import Auth
from database.model import Pet
from schemas.basic_response import BasicResponse
from schemas.pet import GetPetResponse, PostPet

class Operation(Enum):
    ONE_PET = "One pet"
    ALL_PETS = "All pets"

class GetPet:
    def __init__(self, session: Session, id: int | None):
        self._session = session
        self._pet_id = id
        self._operation = Operation | None
    
    def execute(self) -> BasicResponse[list[GetPetResponse] | GetPetResponse]:
        data: list[GetPet] | GetPet
        try:
            self._define_operation()
            if self.operation == Operation.ALL_PETS:
                data = self._get_pets()
            else:
                data = self._get_pet()
            return BasicResponse(data=data)
        except Exception as e:
            raise HTTPException(
                detail=f"Erro interno: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    def _define_operation(self) -> None:
        self.operation = Operation.ONE_PET if self._pet_id else Operation.ALL_PETS
        
    def _get_pets(self) -> list[GetPetResponse]:
        with self._session as db:
            pets = db.query(Pet).all()
            serialized_pets = [GetPetResponse.from_orm(pet) for pet in pets]
            return serialized_pets

    def _get_pet(self) -> GetPetResponse:
        with self._session as db:
            pet: Pet = (
                db.query(Pet).get(self._pet_id)  # type: ignore[assignment]
            )
            if not pet:
                raise HTTPException(
                    detail="Pet não existe", status_code=status.HTTP_404_NOT_FOUND
                )
            serialized_pet = GetPetResponse.from_orm(pet)
            return serialized_pet
        
class CreatePet:
    def __init__(self, session: Session, request: PostPet):
        self.session = session
        self.request = request

    def execute(self) -> BasicResponse[None]:
        try:
            with self.session as session:
                self._create_pet(session)
                session.commit()
                return BasicResponse(message="OK")
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao criar o pet: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_pet(self, session: Session) -> Pet | None:
        pet = Pet(
            name=self.request.name,
            breed = self.request.breed,
            castred = self.request.castred,
            weight = self.request.weight,
            color = self.request.color,
            kind = self.request.kind,
            user_id = self.request.user_id
        )
        session.add(pet)
        session.flush()
        session.refresh(pet)
        return pet