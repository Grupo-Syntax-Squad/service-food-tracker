from enum import Enum
from sqlalchemy.orm import Session

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
    