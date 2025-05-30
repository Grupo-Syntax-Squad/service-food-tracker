from datetime import datetime
from pydantic import BaseModel

class GetPetResponse(BaseModel):
    id: int
    name: str
    breed: str
    weight: float
    color: str
    kind: int
    castred: bool
    enabled: bool

    class Config:
        orm_mode = True
        from_attributes = True

class PostPet(BaseModel):
    name: str
    breed: str | None
    weight: float | None
    color: str | None
    kind: int
    castred: bool | None

    class Config:
        orm_mode = True
        from_attributes = True
