from __future__ import annotations

from os import getenv
from sys import modules
from typing import TypeVar

from dotenv import load_dotenv
from flask_fullstack import Flask, Session, ModBaseMeta
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, Model
from sqlalchemy import MetaData, select
from sqlalchemy.orm import scoped_session, declarative_base
from sqlalchemy.sql import Select

try:
    from greenlet import getcurrent as _ident_func
except ImportError:
    from threading import get_ident as _ident_func

load_dotenv(".env")

app: Flask = Flask(__name__)
app.config["TESTING"] = "pytest" in modules.keys()
app.secrets_from_env("hope it's local")
app.configure_cors()

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


# temp
class ScopedSession(scoped_session, Session):
    pass


class SQLAlchemy(_SQLAlchemy):
    def create_scoped_session(self, options=None):
        if options is None:
            options = {}

        scopefunc = options.pop('scopefunc', _ident_func)
        options.setdefault('query_cls', self.Query)
        return ScopedSession(
            self.create_session(options), scopefunc=scopefunc
        )


db_url: str = getenv("DB_LINK", "sqlite:///../app.db")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db_meta = MetaData(naming_convention=convention)
db = SQLAlchemy(
    app,
    metadata=db_meta,
    model_class=declarative_base(cls=Model, metaclass=ModBaseMeta),
    engine_options={"pool_recycle": 280},  # "echo": True
)

t = TypeVar("t", bound="Base")


class Base(db.Model):  # TODO this is just an idea, redo
    __abstract__ = True

    @classmethod
    def create(cls: type[t], **kwargs) -> t:
        entry = cls(**kwargs)
        db.session.add(entry)
        db.session.flush()
        return entry

    @classmethod
    def select_by_kwargs(cls, *order_by, **kwargs) -> Select:
        if len(order_by) == 0:
            return select(cls).filter_by(**kwargs)
        return select(cls).filter_by(**kwargs).order_by(*order_by)

    @classmethod
    def find_first_by_kwargs(cls: type[t], *order_by, **kwargs) -> t | None:
        return db.session.get_first(cls.select_by_kwargs(*order_by, **kwargs))

    @classmethod
    def find_all_by_kwargs(cls: type[t], *order_by, **kwargs) -> list[t]:
        return db.session.get_all(cls.select_by_kwargs(*order_by, **kwargs))

    @classmethod
    def find_paginated_by_kwargs(
        cls: type[t], offset: int, limit: int, *order_by, **kwargs
    ) -> list[t]:
        return db.session.get_paginated(
            cls.select_by_kwargs(*order_by, **kwargs), offset, limit
        )

    def delete(self) -> None:
        db.session.delete(self)
        db.session.flush()


app.configure_error_handlers(print)
app.config["RESTX_INCLUDE_ALL_MODELS"] = True
