from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.database.model import User
from src.modules.log import Log
from src.schemas.common import BasicResponse
from src.schemas.user import RequestCreateUser, ResponseGetUsers, SchemaCreateUser


class CreateUser:
    def __init__(self, session: Session, request: RequestCreateUser):
        self._log = Log()
        self._session = session
        self._request = request

    def execute(self) -> BasicResponse[None]:
        try:
            self._log.info("Trying to create new user")
            self._get_users()
            self._create_user()
            return BasicResponse()
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error creating new user: %s", e)
            raise HTTPException(
                detail="Erro interno",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_users(self) -> None:
        result = self._session.execute(
            select(User).where(
                or_(
                    User.email == self._request.email,
                    User.cpf_cnpj == self._request.cpf_cnpj,
                )
            )
        )
        users = result.unique().scalars().all()
        if users:
            raise HTTPException(
                detail="Usuário com o email ou cpf ou cnpj informado já existe no sistema",
                status_code=status.HTTP_302_FOUND,
            )

    def _create_user(self) -> None:
        User.add_user(self._session, SchemaCreateUser(**self._request.model_dump()))


class GetUsers:
    def __init__(self, session: Session) -> None:
        self._log = Log()
        self._session = session

    def execute(self) -> BasicResponse[list[ResponseGetUsers]]:
        try:
            self._log.info("Trying to get users")
            self._get_users()
            self._log.info("Users: %s", self._users)
            return BasicResponse(data=self._users)
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error getting users: %s", e)
            raise HTTPException(
                detail="Erro interno",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_users(self) -> None:
        result = self._session.execute(select(User))
        self._users = [
            ResponseGetUsers(
                name=user.name,
                cpf_cnpj=user.cpf_cnpj,
                email=user.email,
                address=user.address,
                phone=user.phone,
            )
            for user in result.unique().scalars().all()
        ]
