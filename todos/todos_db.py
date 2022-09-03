from __future__ import annotations
from datetime import datetime as d

from flask_restx import abort
from sqlalchemy.orm import relationship
from sqlalchemy import Column, select, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Time, Date

from __lib__.flask_fullstack import PydanticModel, Identifiable
from common import Base, sessionmaker


class TodoCategory(Base, Identifiable):
    __tablename__ = "todo_category"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    creator = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        )
    todo = relationship(
        "Todo", back_populates='category', passive_deletes='all'
        )

    MainData = PydanticModel.column_model(id, name)
    RelatedData = PydanticModel.column_model(category_name=name)

    @classmethod
    def get_user_category_by_id(
        cls, session: sessionmaker, id: int, user_id: int
    ) -> TodoCategory | None:
        if not (category := TodoCategory.find_first_by_kwargs(
            session, id=id, creator=user_id)
        ):
            abort(400, "Category does not exist")
        return category

    def update(self, name: str) -> None:
        self.name = name
        return self


class Todo(Base, Identifiable):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey(
        "todo_category.id", ondelete="RESTRICT"), nullable=False
        )
    category = relationship("TodoCategory", back_populates='todo')
    creator = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        )
    date = Column(Date(), nullable=False)
    start_time = Column(Time(timezone=True), nullable=False)
    end_time = Column(Time(timezone=True), nullable=False)

    MainData = PydanticModel.column_model(
        id, name).nest_flat_model(
            TodoCategory.RelatedData,
            parameter_name='category').column_model(date, start_time, end_time)

    @classmethod
    def create(cls, session: sessionmaker, name: str, category: int,
               creator: int, date: d, start_time: d,
               end_time: d) -> Todo | None:
        return super().create(
            session, name=name, category_id=category, creator=creator,
            date=date, start_time=start_time, end_time=end_time)

    @classmethod
    def get_first_task(cls, session: sessionmaker) -> Todo | None:
        return session.get_first(select(cls).filter_by(id=1))

    @classmethod
    def get_user_task_by_id(cls, session: sessionmaker,
                            id: int, user_id: int) -> Todo | None:
        if not (task := Todo.find_first_by_kwargs(
                session, id=id, creator=user_id)):
            abort(400, "Task does not exist")
        return task

    def update(self, name: str, category: int,
               date: d, start_time: d, end_time: d) -> None:
        self.name = name
        self.category = category
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        return self
