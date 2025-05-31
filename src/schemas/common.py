from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BasicResponse[T](BaseModel):
    message: str = "OK"
    data: T | None = None
