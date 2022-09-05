from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Any

from sqlalchemy import Column, select, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String, DateTime, BigInteger, Integer

from __lib__.flask_fullstack import PydanticModel, Identifiable
from .config import Base, sessionmaker


class Message(Base, Identifiable):
    __tablename__ = "messages"
    not_found_text = "Message does not exist"
    unauthorized_error = (401, not_found_text)

    MIN_OFFSET = 0
    MAX_OFFSET = 10000
    MIN_LIMIT = 0
    MAX_LIMIT = 100
    MAX_MESSAGE_TEXT_LENGHT = 1000
    DELETE_MANY_LIMIT = 50
    UPDATE_MESSAGE_DATE_LIMIT = timedelta(hours=24)  # to update message asserts now() - created_at < 24 hours

    # Vital:
    id = Column(BigInteger, primary_key=True, unique=True)
    text = Column(String(MAX_MESSAGE_TEXT_LENGHT), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    MainData = PydanticModel.column_model(id, text, created_at, updated_at)

    @staticmethod
    def limit_value(val: int, min_v: int, max_v: int) -> int:
        return min(max(val, min_v), max_v)

    @classmethod
    def find_by_id(cls, session: sessionmaker, mid: int) -> Message | None:
        return session.get_first(select(cls).filter_by(id=mid))

    @classmethod
    def get_history_with_filter(
        cls, session: sessionmaker, filtered: Any, limit: int, offest: int
    ) -> List[Message] | None:
        return session.get_paginated(
            filtered,
            cls.limit_value(offest, cls.MIN_OFFSET, cls.MAX_OFFSET),
            cls.limit_value(limit, cls.MIN_LIMIT, cls.MAX_LIMIT)
        )

    @classmethod
    def get_history(cls, session: sessionmaker, limit: int, offest: int) -> List[Message] | None:
        return cls.get_history_with_filter(session, select(cls).filter_by(deleted=None), limit, offest)

    @classmethod
    def create(cls, session: sessionmaker, text: str, user_id: int) -> Message | None:
        return super().create(
            session,
            text=text[:cls.MAX_MESSAGE_TEXT_LENGHT],
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @classmethod
    def update(cls, session: sessionmaker, message_id: int, new_text: str) -> Message | None:
        # TODO: add UPDATE_MESSAGE_DATE_LIMIT to if state
        if message := cls.find_by_id(session, message_id):
            message.text = new_text[:cls.MAX_MESSAGE_TEXT_LENGHT]
            message.updated_at = datetime.now()

        return message

    @classmethod
    def delete(cls, session: sessionmaker, message_id: int) -> Message | None:
        if message := cls.find_by_id(session, message_id):
            message.deleted_at = datetime.now()
            message.updated_at = datetime.now()

        return message

    @classmethod
    def delete_many(cls, session: sessionmaker, message_ids: List[int]) -> List[Message] | None:
        # TODO: make delete_many
        pass

    def get_identity(self):
        return self.id
