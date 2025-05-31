from pydantic import BaseModel


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
