from __future__ import annotations

from flask_fullstack import PydanticModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from .config import Base


class TaskTodo(Base):
    __tablename__ = "task_todo"

    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(String(36), nullable=False)
    target: Column = Column(Text, nullable=True)
    is_ready: Column = Column(Boolean, default=False)
    start_task: Column = Column(DateTime, nullable=False)
    end_task: Column = Column(DateTime, nullable=False)
    category_id: Column = Column(Integer, ForeignKey("category_todo.id"))
    user_id: Column = Column(Integer, ForeignKey("users.id"))

    category_todo = relationship("CategoryTodo", back_populates="task_todo")

    MainData = PydanticModel.column_model(
        id, name, target, is_ready, start_task,
        end_task, category_id, user_id
    )

    def __repr__(self):
        return f"name={self.name!r}"


class CategoryTodo(Base):
    __tablename__ = "category_todo"

    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(String(36), nullable=False)

    task_todo = relationship("TaskTodo", back_populates="category_todo")

    MainData = PydanticModel.column_model(id, name)

    def __repr__(self):
        return f"name={self.name!r}"
