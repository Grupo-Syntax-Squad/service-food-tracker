from datetime import datetime
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class UserDataToken(BaseModel):
    user_id: int
    username: str
    email: str
    exp: datetime


class RequestLogin(BaseModel):
    email: str
    password: str
