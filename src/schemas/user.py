from datetime import datetime
from pydantic import BaseModel


class GetUserResponse(BaseModel):
    id: int
    name: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime | None
    last_login: datetime | None
    enabled: bool

    class Config:
        orm_mode = True
        from_attributes = True

class PostUser(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        orm_mode = True
        from_attributes = True