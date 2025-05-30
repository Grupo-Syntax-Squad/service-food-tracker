from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
    select,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    relationship,
)

Base = declarative_base()


class Example(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_onupdate=func.now())


user_pet_association = Table(
    "user_pet",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("pet_id", Integer, ForeignKey("pet.id"), primary_key=True),
)


class User(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))

    pets = relationship(
        "Pet",
        secondary=user_pet_association,
        back_populates="user",
        cascade="all, delete",
        lazy="joined",
    )

    @staticmethod
    def add_user(
        session: Session,
        name: str,
        email: str,
        password: str
    ) -> None:
        user = User(
            name=name,
            email=email,
            password=password
        )
        session.add(user)
        session.commit()

    @staticmethod
    def update_user(
        session: Session,
        user_id: int,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None
    ) -> User | None:
        user: User | None = session.query(User).get(user_id)
        if user:
            if name:
                user.name = name
            if email:
                user.email = email
            if password:
                user.password = password
            session.commit()
            return user
        return None

    @staticmethod
    def delete_user(session: Session, user_id: int) -> None:
        user = select(User).where(User.id == user_id)
        result = session.execute(user).scalars().first()
        if result:
            scheduled = select(ScheduledFeeding).where(ScheduledFeeding.user == user_id)
            result_scheduled = session.execute(scheduled).scalars().all()
            for scheduled in result_scheduled:
                session.delete(scheduled)
                session.commit()
            for pet in result.pets:
                select_pet = select(Pet).where(Pet.id == pet.id)
                result_pet = session.execute(select_pet).scalars().first()
                if result_pet:
                    session.delete(result_pet)
                    session.commit()
            session.delete(result)
            session.commit()


class Pet(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "pet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    breed: Mapped[str] = mapped_column(String)
    weight: Mapped[float] = mapped_column(Float)
    color: Mapped[str] = mapped_column(String)
    kind: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    castred: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))

    user = relationship(
        "User",
        secondary=user_pet_association,
        back_populates="pets",
        cascade="all, delete",
        lazy="joined",
    )

    @staticmethod
    def get_pet_by_id(session: Session, pet_id: int) -> Pet | None:  # noqa: F821
        query = select(Pet).where(Pet.id == pet_id)
        result = session.execute(query)
        return result.scalars().first()

    @staticmethod
    def get_list_pet_by_user_id(session: Session, user_id: int) -> User | None:  # noqa: F821
        query = select(Pet).where(Pet.users == user_id)
        result = session.execute(query)
        return result.scalars().all()

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

    @staticmethod
    def update_pet(session: Session, pet_id: int, **kwargs) -> Pet | None:
        pet = session.get(Pet, pet_id)
        if not pet:
            return None
        for key, value in kwargs.items():
            if hasattr(pet, key) and value is not None:
                setattr(pet, key, value)
        session.commit()
        return pet

    @staticmethod
    def delete_pet(session: Session, pet_id: int) -> bool:
        pet = session.get(Pet, pet_id)
        if pet:
            session.delete(pet)
            session.commit()


class ScheduledFeeding(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "scheduled_feeding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feeding_interval: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))

    user = relationship("User")
    pet = relationship("Pet")

    @staticmethod
    def add_scheduled_feeding(
        session: Session,
        user_id: int,
        pet_id: int,
        feeding_interval: int,
    ) -> None:
        scheduled_feeding = ScheduledFeeding(
            user=user_id,
            pet=pet_id,
            feeding_interval=feeding_interval,
        )
        session.add(scheduled_feeding)
        session.commit()
