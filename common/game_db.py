from __future__ import annotations

from flask_fullstack import UserRole, PydanticModel, Identifiable
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, select, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Integer, String

from . import User
from .config import db, Base


class Sign(Base):
    __tablename__ = 'signs_game'

    id: Column | int = Column(Integer, primary_key=True)
    name: Column | str = Column(String(20), unique=True)
    is_wins: Column | int = Column(Integer, ForeignKey('signs_game.id'), nullable=True)
    move_game: Column | None = relationship("MoveGame")

    @classmethod
    def find_by_name(cls, name):
        return db.get_first(select(cls).filter_by(name=name))

    @classmethod
    def create(cls, name: str, is_wins: int) -> Sign | None:
        return super().create(name=name, is_wins=is_wins)

    BaseModel = PydanticModel.column_model(id, name)

    @classmethod
    def get_all(cls):
        return db.get_all()

    @classmethod
    def find_by_id(cls, id: int):
        return db.get_first(select(cls).filter_by(id=id))


class MoveGame(Base):
    __tablename__ = 'move_game'

    id: Column | int = Column(Integer, primary_key=True)
    user_id: Column | int = Column(Integer, ForeignKey('users.id'))
    sign_id: Column | int = Column(Integer, ForeignKey('signs_game.id'))
    user: relationship = relationship("User")
    sign: relationship = relationship("Sign")
    game_number: Column | int = Column(Integer)
    room_name: Column | str = Column(String(50), nullable=False)
    result: Column | str = Column(String(10), nullable=False)

    BaseModel = PydanticModel.column_model(id, user_id, sign_id)
    CreateBaseModel = PydanticModel.column_model(user_id, sign_id)

    @classmethod
    def create(cls, user_id: int, sign_id: int, room_name: str) -> MoveGame | None:
        game_number = db.get_all(select(cls).filter_by(room_name=room_name, user_id=user_id).count()) + 1
        return super().create(user_id=user_id, sign_id=sign_id, room_name=room_name, game_number=game_number)

    @classmethod
    def find_by_room_name(cls, room_name: str) -> MoveGame | None:
        return db.get_all(select(cls).filter_by(room_name=room_name))
