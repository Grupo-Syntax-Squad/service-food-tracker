import re
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.database.model import User
from src.modules.log import Log
from src.schemas.common import BasicResponse
from src.schemas.user import (
    RequestCreateUser,
    RequestUpdateUser,
    ResponseGetUsers,
    SchemaCreateUser,
    SchemaUserDataValidator,
)


class CreateUser:
    def __init__(self, session: Session, request: RequestCreateUser):
        self._log = Log()
        self._session = session
        self._request = request

    def execute(self) -> BasicResponse[None]:
        try:
            self._log.info("Trying to create new user")
            self._validate()
            self._get_users()
            self._create_user()
            self._log.info("User created")
            return BasicResponse()
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error creating new user: %s", e)
            raise HTTPException(
                detail="Erro interno",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _validate(self) -> None:
        normalized_data, normalized_fields = UserDataValidator(
            SchemaUserDataValidator(
                name=self._request.name,
                cpf_cnpj=self._request.cpf_cnpj,
                email=self._request.email,
                phone=self._request.phone,
                address=self._request.address,
                password=self._request.password,
            )
        ).execute()
        for field in normalized_fields:
            setattr(self._request, field, getattr(normalized_data, field))

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
                detail="Usuário com o email ou cpf/cnpj informado já existe no sistema",
                status_code=status.HTTP_302_FOUND,
            )

    def _create_user(self) -> None:
        User.add_user(self._session, SchemaCreateUser(**self._request.model_dump()))


class UpdateUser:
    def __init__(self, session: Session, request: RequestUpdateUser):
        self._log = Log()
        self._session = session
        self._request = request

    def execute(self) -> BasicResponse[None]:
        try:
            self._log.info("Trying to update user")
            self._validate()
            self._get_user()
            self._update_user()
            self._session.commit()
            self._log.info("User updated successfully")
            return BasicResponse()
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error updating user: %s", e)
            raise HTTPException(
                detail="Erro interno",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _validate(self) -> None:
        normalized_data, normalized_fields = UserDataValidator(
            SchemaUserDataValidator(
                name=self._request.name,
                cpf_cnpj=self._request.cpf_cnpj,
                email=self._request.email,
                phone=self._request.phone,
                address=self._request.address,
                password=self._request.password,
            )
        ).execute()
        for field in normalized_fields:
            setattr(self._request, field, getattr(normalized_data, field))

    def _get_user(self) -> None:
        result = (
            self._session.execute(select(User).where(User.id == self._request.id))
        ).scalar_one_or_none()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )
        self._user: User = result

    def _update_user(self) -> None:
        if self._request.name:
            self._user.name = self._request.name
        if self._request.cpf_cnpj:
            self._user.cpf_cnpj = self._request.cpf_cnpj
        if self._request.email:
            self._user.email = self._request.email
        if self._request.phone:
            self._user.phone = self._request.phone
        if self._request.address:
            self._user.address = self._request.address
        if self._request.password:
            self._user.password = self._request.password
        # TODO: Update user pets
        self._session.add(self._user)
        self._session.flush()


class UserDataValidator:
    def __init__(self, user_data: SchemaUserDataValidator):
        self._log = Log()
        self._user_data = user_data
        self._normalized_fields: list[str] = []

    def execute(self) -> tuple[SchemaUserDataValidator, list[str]]:
        try:
            self._log.info("Validating user data")
            self._normalize_data()
            if self._user_data.name is not None and not self._user_data.name:
                raise ValueError("Nome inválido")
            if self._user_data.cpf_cnpj is not None:
                self._validate_cpf_cnpj()
            if self._user_data.email is not None:
                self._validate_email()
            if self._user_data.phone is not None:
                self._validate_phone()
            if self._user_data.address is not None and not self._user_data.address:
                raise ValueError("Endereço inválido")
            if self._user_data.password is not None and not self._user_data.password:
                raise ValueError("Senha inválida")
            self._log.info("User data validated successfully")
            return self._user_data, self._normalized_fields
        except ValueError as e:
            self._log.info("Invalid user data: %s", e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
        except Exception as e:
            self._log.error("Error validating user data: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno"
            )

    def _normalize_data(self) -> None:
        user_data_dict = self._user_data.model_dump()
        for key, value in user_data_dict.items():
            if isinstance(value, str):
                if key not in self._normalized_fields:
                    self._normalized_fields.append(key)
                setattr(self._user_data, key, value.strip())

    def _validate_cpf_cnpj(self) -> None:
        digits = re.sub(r"\D", "", self._user_data.cpf_cnpj)  # type: ignore[arg-type]
        if len(digits) == 11:
            self.__validate_cpf(digits)
        elif len(digits) == 14:
            self.__validate_cnpj(digits)
        else:
            raise ValueError("CPF ou CNPJ inválido")

    def __validate_cpf(self, cpf: str) -> None:
        if cpf == cpf[0] * len(cpf):
            raise ValueError("CPF inválido")

        for i in [9, 10]:
            value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(i)))
            check = ((value * 10) % 11) % 10
            if check != int(cpf[i]):
                raise ValueError("CPF inválido")

    def __validate_cnpj(self, cnpj: str) -> None:
        if cnpj == cnpj[0] * len(cnpj):
            raise ValueError("CNPJ inválido")
        weights = [
            [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
            [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
        ]
        for i in [0, 1]:
            value = sum(
                int(cnpj[num]) * weights[i][num] for num in range(len(weights[i]))
            )
            check = value % 11
            check = 0 if check < 2 else 11 - check
            if check != int(cnpj[12 + i]):
                raise ValueError("CNPJ inválido")

    def _validate_email(self) -> None:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, self._user_data.email):  # type: ignore[arg-type]
            raise ValueError("Email inválido")

    def _validate_phone(self) -> None:
        digits = re.sub(r"\D", "", self._user_data.phone)  # type: ignore[arg-type]
        if not (10 <= len(digits) <= 11):
            raise ValueError("Número de telefone inválido")


class GetUsers:
    def __init__(self, session: Session) -> None:
        self._log = Log()
        self._session = session

    def execute(self) -> BasicResponse[list[ResponseGetUsers]]:
        try:
            self._log.info("Trying to get users")
            self._get_users()
            self._log.info("Users getted successfully")
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
                id=user.id,
                name=user.name,
                cpf_cnpj=user.cpf_cnpj,
                email=user.email,
                address=user.address,
                phone=user.phone,
            )
            for user in result.unique().scalars().all()
        ]
