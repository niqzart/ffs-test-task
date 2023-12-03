from __future__ import annotations
import string
import random
from sqlalchemy import select as sqlalchemy_select, ForeignKey
from sqlalchemy.sql.sqltypes import String, Enum
from common import Base, db, User
from sqlalchemy.orm import mapped_column, Mapped, relationship
from pydantic_marshals.sqlalchemy import MappedModel
from flask_fullstack import TypeEnum

class Options(TypeEnum):
    ROCK = "ROCK"
    PAPER = "PAPER"
    SCISSORS = "SCISSORS"

    @classmethod
    def list(cls) -> list:
        return [option.value for option in cls]

class GameResults(TypeEnum):
    WIN = 0
    LOSE = 1
    TIE = 2

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_number: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    IdModel = MappedModel.create(columns=[id, room_number])

    @staticmethod
    def generate_room_number() -> str | None:
        room_number = string.ascii_lowercase + string.digits
        return ''.join(random.choices(room_number, k=10))

    @classmethod
    def create(cls, game_id: int, room_number: str) -> Game | None:
        return super().create(id=game_id, room_number=cls.generate_room_number())


    @classmethod
    def get(cls):
        return db.get_all()

    @classmethod
    def find_by_id(cls, game_id: int) -> Game | None:
        return db.get_first(sqlalchemy_select(cls).filter_by(id=game_id))

    @classmethod
    def find_by_room_number(cls, room_number: str) -> Game | None:
        return db.get_first(sqlalchemy_select(cls).filter_by(room_number=room_number))

class GameRounds(Base):
    __tablename__ = "game_rounds"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey('games.id'), nullable=False)
    game: Mapped[Game] = relationship()

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship()

    option: Mapped[Options] = mapped_column(Enum(Options))
    result: Mapped[GameResults] = mapped_column(Enum(GameResults))

    IdModel = MappedModel.create(columns=[id, game_id, user_id])
    OptionModel = MappedModel.create(columns=[option])
    ResultModel = MappedModel.create(columns=[result])

    @classmethod
    def create(cls, game_id: int, user_id: int, option: Options | None, result: GameResults | None) -> 'GameRounds':
        return super().create(game_id=game_id, user_id=user_id, option=option, result=result)

    @classmethod
    def find_by_game_and_user_ids(cls, game_id: int, user_id: int) -> 'GameRounds':
        return db.get_first(sqlalchemy_select(cls).filter_by(game_id=game_id, user_id=user_id))
    
    @classmethod
    def find_opponent(cls, game_id: int, user_id: int) -> 'GameRounds':
        return db.get_first(
            sqlalchemy_select(cls)
            .filter_by(game_id=game_id)
            .filter(GameRounds.user_id != user_id)
        )

    @classmethod
    def get_user_all_game(cls, user_id: int) -> list['GameRounds']:
        return db.session.execute(sqlalchemy_select(cls).filter_by(user_id=user_id)).all()
    


