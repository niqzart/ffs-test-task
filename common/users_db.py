from __future__ import annotations

from flask_fullstack import UserRole, Identifiable
from passlib.hash import pbkdf2_sha256
from pydantic_marshals.sqlalchemy import MappedModel
from sqlalchemy import select
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql.sqltypes import String

from .config import Base, db


class BlockedToken(Base):
    __tablename__ = "blocked_tokes"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    jti: Mapped[str] = mapped_column(String(36))

    @classmethod
    def find_by_jti(cls, jti) -> BlockedToken | None:
        return db.get_first(select(cls).filter_by(jti=jti))


class User(Base, UserRole, Identifiable):
    __tablename__ = "users"
    not_found_text = "User does not exist"
    unauthorized_error = (401, not_found_text)

    @staticmethod
    def generate_hash(password) -> str:
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify_hash(password, hashed) -> bool:
        return pbkdf2_sha256.verify(password, hashed)

    # Vital:
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))

    MainData = MappedModel.create(columns=[id, username])

    @classmethod
    def find_by_id(cls, entry_id: int) -> User | None:
        return db.get_first(select(cls).filter_by(id=entry_id))

    @classmethod
    def find_by_identity(cls, identity: int) -> User | None:
        return cls.find_by_id(identity)

    @classmethod
    def find_by_username(cls, username: str) -> User | None:
        return db.get_first(select(cls).filter_by(username=username))

    @classmethod
    def create(cls, username: str, password: str) -> User | None:
        return super().create(username=username, password=cls.generate_hash(password))

    def get_identity(self) -> int:
        return self.id


UserRole.default_role = User
