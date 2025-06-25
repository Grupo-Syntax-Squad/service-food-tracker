from pydantic import BaseModel


class GetPetResponse(BaseModel):
    pet_id: int
    name: str
    breed: str
    weight: float
    color: str
    kind: int
    castred: bool
    enabled: bool


class PostPet(BaseModel):
    user_id: int
    name: str
    breed: str | None = None
    weight: float | None = None
    color: str | None = None
    kind: int
    castred: bool | None = None

    class Config:
        orm_mode = True
        from_attributes = True


class PutPet(BaseModel):
    name: str
    breed: str | None
    weight: float | None
    color: str | None
    kind: int
    castred: bool | None

    class Config:
        orm_mode = True
        from_attributes = True

