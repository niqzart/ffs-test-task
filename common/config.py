from __future__ import annotations

from os import getenv
from sys import modules

from dotenv import load_dotenv
from flask_fullstack import Flask, SQLAlchemy
from flask_fullstack.utils.sqlalchemy import CustomModel, ModBaseMeta
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import declarative_base

load_dotenv(".env")

app: Flask = Flask(__name__)
app.config["TESTING"] = "pytest" in modules.keys()
app.secrets_from_env("hope it's local")
app.configure_cors()


class DeclaredBase(CustomModel):
    __table__: Table
    metadata = MetaData(naming_convention=SQLAlchemy.DEFAULT_CONVENTION)


db_url: str = getenv("DB_LINK", "sqlite:///../app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
Base = declarative_base(cls=DeclaredBase, metaclass=ModBaseMeta)
db = SQLAlchemy(app, db_url, model_class=Base)  # "echo": True

if db_url.startswith("sqlite"):  # pragma: no coverage
    from sqlalchemy.event import listen


    def set_sqlite_pragma(dbapi_connection, *_):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


    with app.app_context():
        listen(db.engine, "connect", set_sqlite_pragma)

app.configure_error_handlers(print)
app.config["RESTX_INCLUDE_ALL_MODELS"] = True
