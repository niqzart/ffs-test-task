from __future__ import annotations

from flask_fullstack import UserRole, PydanticModel, Identifiable
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, select, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Integer, String

from .config import db, Base

# Base = declarative_base()


class Sign(Base):
    __tablename__ = 'signs_game'

    id: Column | int = Column(Integer, primary_key=True)
    name: Column | str = Column(String(20), unique=True)
    is_wins: Column | int = Column(Integer, ForeignKey('sign_game.id'), nullable=True)

    @classmethod
    def find_by_name(cls, name):
        return db.get_first(select(cls).filter_by(name=name))

    @classmethod
    def create(cls, name: str, is_wins: int) -> Sign | None:
        return super().create(name=name, is_wins=is_wins)
