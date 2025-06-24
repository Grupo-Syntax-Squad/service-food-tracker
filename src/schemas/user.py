from pydantic import BaseModel

from src.schemas.pet import GetPetResponse


class RequestCreateUser(BaseModel):
    name: str
    cpf_cnpj: str
    email: str
    phone: str
    address: str
    password: str


class ResponseGetUser(BaseModel):
    id: int
    name: str
    cpf_cnpj: str
    email: str
    phone: str
    address: str
    pets: list[GetPetResponse]

    class Config:
        orm_mode = True


class RequestUpdateUser(BaseModel):
    id: int
    name: str | None = None
    cpf_cnpj: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    password: str | None = None
    pets: list[int] | None = None


class SchemaUserDataValidator(BaseModel):
    name: str | None
    cpf_cnpj: str | None
    email: str | None
    phone: str | None
    address: str | None
    password: str | None


class SchemaCreateUser(BaseModel):
    name: str
    cpf_cnpj: str
    email: str
    password: str
    address: str
    phone: str


class SchemaUpdateUser(BaseModel):
    id: int
    name: str | None = None
    cpf_cnpj: str | None = None
    email: str | None = None
    password: str | None = None
    address: str | None = None
    phone: str | None = None
    email_verified: bool | None = None
