from pydantic import BaseModel


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