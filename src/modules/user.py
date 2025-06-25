import re
from fastapi import HTTPException, status
from src.schemas.pet import GetPetResponse, PostPet
from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session, joinedload

from src.database.model import Pet, User
from src.modules.log import Log
from src.schemas.basic_response import BasicResponse
from src.schemas.user import (
    RequestCreateUser,
    RequestUpdateUser,
    ResponseGetUser,
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
            self._log.error("Error creating new user: %s", str(e))
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
            self._session.rollback()
            raise e
        except Exception as e:
            self._session.rollback()
            self._log.error("Error updating user: %s", str(e))
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
        self.__validate_pets()

    def __validate_pets(self) -> None:
        if self._request.pets is not None:
            database_pets_ids = set([pet.id for pet in self.__get_pets()])
            request_pets_set = set(self._request.pets)
            missing_pets = [
                str(pet_id) for pet_id in (request_pets_set - database_pets_ids)
            ]
            if missing_pets:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Os pets com os ids: {','.join(missing_pets)} não existem",
                )

    def __get_pets(self) -> list[Pet]:
        result = self._session.execute(
            select(Pet).where(Pet.id.in_(self._request.pets))  # type: ignore[arg-type]
        )
        return list(result.scalars().all())

    def _get_user(self) -> None:
        result = (
            (self._session.execute(select(User).where(User.id == self._request.id)))
            .unique()
            .scalar_one_or_none()
        )
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
        if self._request.pets is not None:
            UserPetsHandler(
                self._session, self._request.id, self._request.pets
            ).execute()
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


class UserPetsHandler:
    def __init__(self, session: Session, user_id: int, new_pets_list: list[int]):
        self._log = Log()
        self._session = session
        self._user_id = user_id
        self._new_pets_list = set(new_pets_list)

    def execute(self) -> None:
        try:
            self._log.info("Trying to handler user pets")
            enabled_user_pets, disabled_user_pets = self._get_all_user_pet_relations()

            enable_user_pets = disabled_user_pets & self._new_pets_list
            disable_user_pets = enabled_user_pets - self._new_pets_list

            self._enable_user_pets(enable_user_pets)
            self._disable_user_pets(disable_user_pets)
            self._log.info("Handled user pets successfully")
        except HTTPException as e:
            raise e
        except Exception as e:
            self._log.error("Error handling user pets: %s", str(e))
            raise e

    def _get_all_user_pet_relations(self) -> tuple[set[int], set[int]]:
        all_user_pets = (
            self._session.execute(select(Pet).where(Pet.user_id == self._user_id))
            .scalars()
            .all()
        )

        enabled_user_pets_ids = set(
            [pet.id for pet in all_user_pets if pet.enabled is True]
        )
        disabled_user_pets_ids = set(
            [pet.id for pet in all_user_pets if pet.enabled is False]
        )
        return (enabled_user_pets_ids, disabled_user_pets_ids)

    def _enable_user_pets(self, pet_ids: set[int]) -> None:
        self._session.execute(
            update(Pet).where(Pet.id.in_(pet_ids)).values(enabled=True)
        )
        self._session.flush()

    def _disable_user_pets(self, pet_ids: set[int]) -> None:
        self._session.execute(
            update(Pet).where(Pet.id.in_(pet_ids)).values(enabled=False)
        )
        self._session.flush()


class GetUsers:
    def __init__(self, session: Session) -> None:
        self._log = Log()
        self._session = session

    def execute(self) -> BasicResponse[list[ResponseGetUser]]:
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
        result = self._session.execute(
            select(User).options(joinedload(User.pets)).where(User.enabled)
        )
        self._users = [
            ResponseGetUser(
                id=user.id,
                name=user.name,
                cpf_cnpj=user.cpf_cnpj,
                email=user.email,
                address=user.address,
                phone=user.phone,
                pets=[
                    GetPetResponse(
                        pet_id=pet.id,
                        name=pet.name,
                        breed=pet.breed,
                        weight=pet.weight,
                        color=pet.color,
                        kind=pet.kind,
                        castred=pet.castred,
                        enabled=pet.enabled,
                    )
                    for pet in user.pets
                ],
            )
            for user in result.unique().scalars().all()
        ]


class DeleteUser:
    def __init__(self, session: Session, user_id: int):
        self._log = Log()
        self._session = session
        self._user_id = user_id

    def execute(self) -> BasicResponse[None]:
        try:
            self._log.info("Trying to delete user")
            self._get_user()
            self._user.enabled = False
            self._session.commit()
            self._log.info("User deleted successfully")
            return BasicResponse()
        except HTTPException as e:
            self._session.rollback()
            raise e
        except Exception as e:
            self._session.rollback()
            self._log.error("Error deleting user: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno"
            )

    def _get_user(self) -> None:
        result = self._session.execute(
            select(User).where(User.id == self._user_id)
        ).scalar_one_or_none()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )
        self._user = result


class UpdateUserPets:
    def __init__(self, session: Session, user_id: int):
        self._session = session
        self._user_id = user_id

    def _load_user(self) -> None:
        result = self._session.get(User, self._user_id)
        if result is None:
            raise HTTPException(
                detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND
            )
        self._user = result

    def add_pet(self, pet_data: PostPet) -> BasicResponse[None]:
        try:
            self._load_user()
            pet = Pet(
                name=pet_data.name,
                breed=pet_data.breed,
                castred=pet_data.castred,
                weight=pet_data.weight,
                color=pet_data.color,
                kind=pet_data.kind,
                user_id=self._user.id,
            )
            self._session.add(pet)
            self._session.commit()
            return BasicResponse(message="Pet adicionado com sucesso.")
        except Exception as e:
            self._session.rollback()
            raise HTTPException(
                detail=f"Erro ao adicionar pet: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def remove_pet(self, pet_id: int) -> BasicResponse[None]:
        try:
            self._load_user()
            pet = self._session.get(Pet, pet_id)
            if not pet or pet.user_id != self._user_id:
                raise HTTPException(
                    detail="Pet não encontrado ou não pertence ao usuário.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            self._session.delete(pet)
            self._session.commit()
            return BasicResponse(message="Pet removido com sucesso.")
        except HTTPException:
            raise
        except Exception as e:
            self._session.rollback()
            raise HTTPException(
                detail=f"Erro ao remover pet: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
