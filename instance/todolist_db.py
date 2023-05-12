from __future__ import annotations

import datetime

from flask_fullstack import Identifiable, PydanticModel
from sqlalchemy import Column, ForeignKey, select, sql
from sqlalchemy.sql.sqltypes import DateTime, Integer, Text

from common import Base, User, db


class Task(Base, Identifiable):
    __tablename__ = "tasks"
    not_found_text = "Task does not exist"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    date_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)

    creator_id = Column(Integer, ForeignKey(User.id), nullable=False)

    created = Column(DateTime, server_default=sql.func.now(), nullable=False)
    changed = Column(
        DateTime,
        server_default=sql.func.now(),
        server_onupdate=sql.func.now(),
        nullable=False,
    )

    IndexModel = PydanticModel.column_model(title, category, date_time, duration)
    CreationBaseModel = IndexModel.column_model(creator_id)
    BaseModel = IndexModel.column_model(id)

    @classmethod
    def find_by_id(cls, entry_id: int) -> Task | None:
        return cls.find_first_by_kwargs(id=entry_id)

    @classmethod
    def find_all_tasks_by_creator_id(cls, entry_id: int) -> list[Task] | None:
        return db.get_all(select(cls).filter_by(creator_id=entry_id))

    @classmethod
    def create(
        cls,
        title: str,
        category: str,
        date_time: datetime.datetime,
        duration: int,
        creator_id: int,
    ) -> Task:
        return super().create(
            title=title,
            category=category,
            date_time=date_time,
            duration=duration,
            creator_id=creator_id,
        )
