from datetime import time
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.model import Pet, ScheduledFeeding
from src.schemas.scheduled_feeding import RequestCreateScheduledFeeding
from src.schemas.common import BasicResponse
from src.modules.log import Log


class CreateScheduledFeeding:
    def __init__(
        self, session: Session, request: RequestCreateScheduledFeeding
    ) -> None:
        self._log = Log()
        self._session = session
        self._request = request

    def execute(self) -> BasicResponse[None]:
        try:
            self._log.info("Trying to create scheduled feeding")
            pet = self._get_pet(self._request.pet_id)
            self._verify_if_pet_scheduled_feeding_already_exists(
                pet, self._request.feeding_time
            )
            self._session.commit()
            self._log.info("Scheduled feeding created succesfully")
            return BasicResponse(message="Alimentação agendada criada com sucesso")
        except Exception as e:
            self._session.rollback()
            self._log.error("Error creating scheduled feeding: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno"
            )

    def _get_pet(self, pet_id: int) -> Pet:
        result: Pet | None = (
            self._session.execute(select(Pet).where(Pet.id == pet_id))
        ).scalar_one_or_none()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pet não encontrado"
            )
        return result

    def _verify_if_pet_scheduled_feeding_already_exists(
        self, pet: Pet, feeding_time: time
    ) -> None:
        result: ScheduledFeeding | None = (
            self._session.execute(
                select(ScheduledFeeding).where(
                    ScheduledFeeding.pet_id == pet.id,
                    ScheduledFeeding.feeding_time == feeding_time,
                    ScheduledFeeding.enabled,
                )
            )
        ).scalar_one_or_none()
        if result is not None:
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="A alimentação agendada já existe",
            )

    def _create_scheduled_feeding(self, pet: Pet, feeding_time: time) -> None:
        scheduled_feeding = ScheduledFeeding(pet_id=pet.id, feeding_time=feeding_time)
        self._session.add(scheduled_feeding)
        self._session.flush()
