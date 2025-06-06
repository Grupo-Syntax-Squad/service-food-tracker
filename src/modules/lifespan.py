from config import Settings
from src.database import DatabaseConnection
from src.database.model import User
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
                self._create_default_user()
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

    def _create_default_user(self) -> None:
        new_default_user = User(
            name="Default user",
            cpf_cnpj="65508999078",
            email=settings.default_user_email,
            password=AuthHandler()._hash_password(settings.default_user_password),
            address="Default user address",
            phone=74994939050,
        )
        self._session.add(new_default_user)
        self._session.commit()
