from __future__ import annotations

from typing import TypeVar
from flask_fullstack import PydanticModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from .config import Base
from common import db, get_datetime

t = TypeVar("t", bound="TaskTodo")


class TaskTodo(Base):
    __tablename__ = "task_todo"
    not_found_text = 'Task does not exist'

    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(String(36), nullable=False)
    description: Column = Column(Text, nullable=True)
    is_ready: Column = Column(Boolean, default=False)
    start_task: Column = Column(DateTime, nullable=False)
    end_task: Column = Column(DateTime, nullable=False)
    category_id: Column = Column(Integer, ForeignKey("category_todo.id"))
    user_id: Column = Column(Integer, ForeignKey("users.id"))

    category_todo = relationship("CategoryTodo", back_populates="task_todo")

    BaseModel = PydanticModel.column_model(id)
    CreationBaseModel = PydanticModel.column_model(
        name, description, start_task,
        end_task, category_id
    )
    IndexModel = PydanticModel.column_model(
        name, description,
        is_ready,
        start_task, end_task, category_id, user_id
    ).combine_with(BaseModel)

    @classmethod
    def get_all(cls: type[t], user_id: int) -> list[t]:
        return db.session.query(cls).filter_by(user_id=user_id).join(cls.category_todo).all()

    @staticmethod
    def change_values(task, **kwargs) -> TaskTodo:
        for key, value in kwargs.items():
            if value is not None and key != 'task_name':
                if key == 'start_task' or 'end_task':
                    setattr(task, key, get_datetime(value))
                setattr(task, key, value)
        return task

    def __repr__(self):
        return f"name={self.name!r}"


class CategoryTodo(Base):
    __tablename__ = "category_todo"

    not_found_text = "Category does not exist"

    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(String(36), nullable=False)
    user_id: Column = Column(Integer, ForeignKey("users.id"))

    task_todo = relationship("TaskTodo", back_populates="category_todo")

    BaseModel = PydanticModel.column_model(id)
    CreationBaseModel = PydanticModel.column_model(name, user_id)
    IndexModel = BaseModel.combine_with(model=CreationBaseModel)

    def __repr__(self):
        return f"name={self.name!r}"
