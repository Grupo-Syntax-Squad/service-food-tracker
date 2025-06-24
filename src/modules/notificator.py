from firebase_admin import credentials, messaging
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.model import Pet, User
from src.modules.log import Log
from config import settings


class UserNotificator:
    def __init__(self, session: Session) -> None:
        self._log = Log()
        self._session = session
        self._credentials = credentials.Certificate(settings.firebase_credentials_path)

    def notificate(self, pet: Pet) -> None:
        try:
            self._log.info("Trying to notificate user to feed your pet")
            user = self._get_pet_user(pet)
            message = self._initialize_message(pet, user)
            response = messaging.send(message)
            self._log.info("Notification sent successfuly: %s", response)
        except Exception as e:
            self._log.error(
                "Error trying to notificate user to feed your pet: %s", str(e)
            )

    def _get_pet_user(self, pet: Pet) -> User:
        result = (
            self._session.execute(select(User).where(User.id == pet.user_id))
        ).scalar_one_or_none()
        if result is None:
            raise RuntimeError("Pet user not found")
        return result

    def _initialize_message(self, pet: Pet, user: User) -> messaging.Message:
        return messaging.Message(
            notification=messaging.Notification(
                title="Hora de alimentar seu Pet",
                body=f"Está na hora de alimentar o(a) {pet.name}",
            ),
            token=user.device_token,
        )
