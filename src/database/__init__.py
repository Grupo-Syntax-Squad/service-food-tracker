from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import Settings

settings = Settings()


class DatabaseConnection:
    def __init__(self) -> None:
        self._engine = create_engine(settings.database_url, echo=True)
        self._sessionmaker = sessionmaker(bind=self._engine)

    def get_db_session(self) -> Generator[Session, None, None]:
        session = self._sessionmaker()
        try:
            yield session
        finally:
            session.close()
