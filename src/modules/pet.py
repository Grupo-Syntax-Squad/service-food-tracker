from enum import Enum
from fastapi import HTTPException, status
from sqlalchemy import select
from src.modules.log import Log
from sqlalchemy.orm import Session

from src.database.model import Pet
from src.schemas.basic_response import BasicResponse
from src.schemas.pet import GetPetResponse, PostPet, PutPet


class Operation(Enum):
    ONE_PET = "One pet"
    ALL_PETS = "All pets"


class GetPet:
    def __init__(self, session: Session, pet_id: int | None = None):
        self._log = Log()
        self._session = session
        self._pet_id = pet_id
        self._operation = Operation | None

    def execute(
        self,
    ) -> BasicResponse[list[GetPetResponse]] | BasicResponse[GetPetResponse]:
        data: list[GetPetResponse] | GetPetResponse
        try:
            self._log.info("Trying to get pets")
            self._define_operation()
            if self.operation == Operation.ALL_PETS:
                data = self._get_pets()
            else:
                data = self._get_pet()
            self._log.info("Pets getted successfully")
            return BasicResponse(data=data)
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error getting pets: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno"
            )

    def _define_operation(self) -> None:
        self.operation = Operation.ONE_PET if self._pet_id else Operation.ALL_PETS

    def _get_pets(self) -> list[GetPetResponse]:
        with self._session as db:
            pets = db.query(Pet).all()
            serialized_pets = [self._build_pet_response(pet) for pet in pets]
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
            serialized_pet = self._build_pet_response(pet)
            return serialized_pet

    def _build_pet_response(self, pet: Pet) -> GetPetResponse:
        return GetPetResponse(
            pet_id=pet.id,
            name=pet.name,
            breed=pet.breed,
            weight=pet.weight,
            color=pet.color,
            kind=pet.kind,
            castred=pet.castred,
            enabled=pet.enabled,
        )


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
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao criar o pet: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_pet(self, session: Session) -> Pet | None:
        pet = Pet(
            name=self.request.name,
            breed=self.request.breed,
            castred=self.request.castred,
            weight=self.request.weight,
            color=self.request.color,
            kind=self.request.kind,
            user_id=self.request.user_id,
        )
        session.add(pet)
        session.flush()
        session.refresh(pet)
        return pet


class UpdatePet:
    def __init__(self, session: Session, request: PutPet, id: int | None = None):
        try:
            self._log = Log()
            self._session = session
            self._pet_id = id
            self._request = request
            print(self._request)
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error updating pet: %s", str(e))
            raise HTTPException(
                detail="Erro interno",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def execute(self) -> BasicResponse[None]:
        self._get_pet()
        self._update_pet()
        self._session.commit()
        self._log.info("Pet updated successfully")
        return BasicResponse()

    def _get_pet(self) -> None:
        result = (
            (self._session.execute(select(Pet).where(Pet.id == self._pet_id)))
            .unique()
            .scalar_one_or_none()
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pet não encontrado"
            )
        self._pet: Pet = result

    def _update_pet(self) -> None:
        if self._request.name:
            self._pet.name = self._request.name
        if self._request.breed:
            self._pet.breed = self._request.breed
        if self._request.kind:
            self._pet.kind = self._request.kind
        if self._request.castred is not None:
            self._pet.castred = self._request.castred
        if self._request.color:
            self._pet.color = self._request.color
        if self._request.weight:
            self._pet.weight = self._request.weight
        self._session.add(self._pet)
        self._session.flush()
