from sqlalchemy.orm import Session


class CreateUser:
    def __init__(self, session: Session):
        self._session = session

    def execute(self) -> None: ...
