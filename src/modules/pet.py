from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.model import Pet
from src.modules.log import Log
from src.schemas.common import BasicResponse
from src.schemas.pet import PutPet

class UpdatePet:
    def __init__(self, request: PutPet, session: Session, id: int | None = None):
        try:
            self._log = Log()
            self._session = session
            self._pet_id = id
            self._request = request
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error creating new pet: %s", str(e))
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
            self._session.execute(select(Pet).where(Pet.id == self._pet_id))
        ).scalar_one_or_none()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pet não encontrado"
            )
        self._pet: Pet = result

    def _update_pet(self):
        if self._request.name:
            self._pet.name = self._request.name
        if self._request.breed:
            self._pet.name = self._request.breed
        if self._request.kind:
            self._pet.name = self._request.kind
        if self._request.castred:
            self._pet.name = self._request.castred
        if self._request.color:
            self._pet.name = self._request.color
        if self._request.weight:
            self._pet.name = self._request.weight
        self._session.add(self._pet)
        self._session.flush()
