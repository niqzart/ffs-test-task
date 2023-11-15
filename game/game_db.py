from __future__ import annotations
import string
import random
import sqlalchemy
from flask_fullstack import TypeEnum
from sqlalchemy import select, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Enum
from common import Base, db, User
from sqlalchemy.orm import mapped_column, Mapped, relationship, sessionmaker
from pydantic_marshals.sqlalchemy import MappedModel


class Options(TypeEnum):
    __tablename__ = 'options_table'

    ROCK = "ROCK"
    PAPER = "PAPER"
    SCISSORS = "SCISSORS"

    @classmethod
    def list(self) -> list:
        return [option.value for option in Options]


class GameResults(TypeEnum):
    WIN = 0
    LOSE = 1
    TIE = 2


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_number: Mapped[int]  = mapped_column(String(10), unique=True, nullable=False)

    IdModel = MappedModel.create(columns=[id, room_number])

    @staticmethod
    def generate_room_number() -> str | None:
        characters = string.ascii_lowercase + string.digits
        return ''.join(random.choices(characters, k=10))

    @classmethod
    def create(cls, game_id: int = None) -> Game | None:
        room_number = cls.generate_room_number()
        return super().create(room_number=room_number, id=game_id)

    @classmethod
    def get_all(cls):
        return db.get_all()

    @classmethod
    def find_by_id(cls, game_id: int):
        return db.get_first(select(cls).filter_by(id=game_id))

    @classmethod
    def find_by_room_number(cls, room_number: str) -> Game | None:
        return db.get_first(select(cls).filter_by(room_number=room_number))


class GameModel(Base):
    __tablename__ = "game_rounds"

    id: Mapped[int] = mapped_column(primary_key=True)

    game_id: Mapped[int] = mapped_column(ForeignKey('games.id'), nullable=False)
    game: Mapped[Game] = relationship()

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped[User] = relationship()

    option: Mapped[Options] = mapped_column(sqlalchemy.Enum(Options))
    result: Mapped[GameResults] = mapped_column((sqlalchemy.Enum(GameResults)))

    IdModel = MappedModel.create(columns=[id, game_id, user_id, result])
    OptionModel = MappedModel.create(columns=[option])
    ResultModel = MappedModel.create(columns=[result])

    @classmethod
    def create(cls, game_id: int, user_id: int, option: str = None, result: str = None) -> GameModel | None:
        return super().create(
            game_id=game_id,
            user_id=user_id,
            option=option,
            result=result)

    @classmethod
    def find_by_game_and_user_ids(cls, game_id: int, user_id: int) -> GameModel | None:
        return db.get_first(select(cls).filter_by(
            game_id=game_id,
            user_id=user_id))
    
    @classmethod
    def find_enemy(cls, game_id: int, user_id: int) -> GameModel | None:
        return db.get_first(select(cls).where(
            game_id == game_id,
            user_id != user_id))
    
    @classmethod
    def get_all(cls, user_id: int) -> list | None:
        return db.session.query(cls).filter_by(user_id=user_id).all()
