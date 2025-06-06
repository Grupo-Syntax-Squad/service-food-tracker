from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    DeclarativeBase,
)

from src.schemas.user import SchemaCreateUser

Base: DeclarativeBase = declarative_base()


class Example(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_onupdate=func.now())


class User(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    cpf_cnpj: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    email_verified: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))

    @staticmethod
    def add_user(session: Session, new_user: SchemaCreateUser) -> None:
        user = User(
            name=new_user.name,
            cpf_cnpj=new_user.cpf_cnpj,
            email=new_user.email,
            password=new_user.password,
            address=new_user.address,
            phone=new_user.phone,
        )
        session.add(user)
        session.commit()


class Pet(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "pet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    name: Mapped[str] = mapped_column(String)
    breed: Mapped[str] = mapped_column(String)
    weight: Mapped[float] = mapped_column(Float)
    color: Mapped[str] = mapped_column(String)
    kind: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    castred: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))


class ScheduledFeeding(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "scheduled_feeding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feeding_interval: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    pet_id: Mapped[int] = mapped_column(ForeignKey("pet.id"))
