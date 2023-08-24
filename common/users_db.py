from __future__ import annotations

from flask_fullstack import UserRole, PydanticModel, Identifiable
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, select
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer, String

from .config import Base, db


class BlockedToken(Base):
    __tablename__ = "blocked_tokes"

    id = Column(Integer, primary_key=True, unique=True)
    jti = Column(String(36), nullable=False)

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
    id: Column | int = Column(Integer, primary_key=True)
    username: Column | str = Column(String(100), unique=True, nullable=False)
    password: Column | str = Column(String(100), nullable=False)
    move_game: relationship = relationship("MoveGame", back_populates='user')

    MainData = PydanticModel.column_model(id, username)

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
