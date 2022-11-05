from __future__ import annotations

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from .config import Base


class TaskTodo(Base):
    __tablename__ = "task_todo"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(36), nullable=False)
    target = Column(Text, nullable=True)
    is_ready = Column(Boolean, default=False)
    start_task = Column(DateTime, nullable=False)
    end_task = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey("category_todo.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    category_todo = relationship("CategoryTodo", back_populates="task_todo")

    def __repr__(self):
        return f"name={self.name!r}"


class CategoryTodo(Base):
    __tablename__ = "category_todo"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(36), nullable=False)

    task_todo = relationship("TaskTodo", back_populates="category_todo")

    def __repr__(self):
        return f"name={self.name!r}"
