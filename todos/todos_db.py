from __future__ import annotations

from datetime import datetime

from flask_fullstack import Identifiable, PydanticModel
from sqlalchemy import Column, select, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, DateTime

from common import Base, User, db


class Todo(Base, Identifiable):
    __tablename__ = "todos"

    id: Column | int = Column(Integer, primary_key=True, unique=True)
    task: Column | str = Column(String(100), nullable=False)
    category: Column | str = Column(String(100), nullable=False)
    date: Column | datetime = Column(DateTime, nullable=False)
    duration: Column | int = Column(Integer, nullable=False)

    user_id: Column | int = Column(Integer, ForeignKey(User.id), nullable=False)

    IndexModel = PydanticModel.column_model(id, task, category, date, duration, user_id)
    BaseModel = PydanticModel.column_model(task, category, date, duration, user_id)
    DeleteModel = PydanticModel.column_model(id, user_id)

    @classmethod
    def create(
            cls,
            task: str,
            category: str,
            date: datetime,
            duration: int,
            user_id: int,
    ) -> Todo | None:
        return super().create(
            task=task,
            category=category,
            date=date,
            duration=duration,
            user_id=user_id,
        )

    @classmethod
    def get_by_id(cls, todo_id: int, user_id: int) -> Todo | None:
        return db.get_first(select(cls).filter_by(id=todo_id, user_id=user_id))

    @classmethod
    def find_by_user_id(cls, user_id: int) -> list[Todo]:
        return db.get_all(select(cls).filter_by(user_id=user_id))
