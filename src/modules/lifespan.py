from config import Settings
from src.database import DatabaseConnection
from src.database.model import Pet, User
from src.modules.auth_handler import AuthHandler
from src.modules.log import Log

settings = Settings()


class LifespanHandler:
    def execute(self) -> None:
        self._log = Log()
        try:
            self._log.info("Executing lifespan events")
            session_generator = DatabaseConnection().get_db_session()
            self._session = next(session_generator)
            default_user = self._get_default_user()
            if not default_user:
                default_user = self._create_default_user()
            default_pet = self._get_user_pet(default_user)
            if not default_pet:
                self._create_user_pet(default_user)
            self._log.info("Lifespan events executed")
        except Exception as e:
            self._log.error("Error executing lifespan events: %s", str(e))
            raise e
        finally:
            try:
                session_generator.close()
            except Exception as close_error:
                self._log.error("Error closing DB session: %s", str(close_error))

    def _get_default_user(self) -> User | None:
        return (
            self._session.query(User)
            .filter(User.email == settings.default_user_email)
            .first()
        )

    def _create_default_user(self) -> User:
        new_default_user = User(
            name="User",
            cpf_cnpj="65508999078",
            email=settings.default_user_email,
            password=AuthHandler()._hash_password(settings.default_user_password),
            address="Default user address",
            phone=74994939050,
            device_token=settings.default_user_device_token,
        )
        self._log.debug(
            "Default user device token: %s", settings.default_user_device_token
        )
        self._session.add(new_default_user)
        self._session.commit()
        return new_default_user

    def _get_user_pet(self, user: User) -> Pet | None:
        return self._session.query(Pet).filter(Pet.user_id == user.id).first()

    def _create_user_pet(self, user: User) -> None:
        new_default_pet = Pet(
            user_id=user.id,
            name=settings.default_pet_name,
            breed=settings.default_pet_breed,
            weight=8,
            color=settings.default_pet_color,
            kind=1,
        )
        self._session.add(new_default_pet)
        self._session.commit()
