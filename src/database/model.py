from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
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
    relationship,
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
    cpf_cnpj: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
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

    pets = relationship(
        "Pet", back_populates="owner", cascade="all, delete", lazy="joined"
    )

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
    name: Mapped[str] = mapped_column(String)
    breed: Mapped[str] = mapped_column(String, nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=True)
    color: Mapped[str] = mapped_column(String, nullable=True)
    kind: Mapped[int] = mapped_column(Integer)
    castred: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    owner = relationship("User", back_populates="pets", lazy="joined")

    @staticmethod
    def add_pet(
        session: Session,
        name: str,
        breed: str,
        weight: float,
        color: str,
        kind: list[int],
        user_id: int | None = None,
    ) -> "Pet":
        pet = Pet(
            name=name,
            breed=breed,
            weight=weight,
            color=color,
            kind=kind,
        )
        if user_id:
            user = session.get(User, user_id)
            if user:
                pet.users.append(user)
        session.add(pet)
        session.commit()
        return pet

    @staticmethod
    def update_pet(session: Session, pet_id: int, **kwargs: Any) -> Pet | None:
        pet = session.get(Pet, pet_id)
        if not pet:
            return None
        for key, value in kwargs.items():
            if hasattr(pet, key) and value is not None:
                setattr(pet, key, value)
        session.commit()
        return pet

    @staticmethod
    def delete_pet(session: Session, pet_id: int) -> None:
        pet = session.get(Pet, pet_id)
        if pet:
            session.delete(pet)
            session.commit()


class ScheduledFeeding(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "scheduled_feeding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feeding_interval: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    pet_id: Mapped[int] = mapped_column(ForeignKey("pet.id"))
