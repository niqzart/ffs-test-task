from collections.abc import Iterator

import pytest
from flask_fullstack import FlaskTestClient, SocketIOTestClient

from main import app

app.test_client_class = FlaskTestClient


@pytest.fixture(autouse=True)
def application_context() -> Iterator[None]:
    with app.app_context():
        yield


@pytest.fixture()
def client() -> Iterator[FlaskTestClient]:
    app.debug = True
    with app.test_client() as client:
        yield client


@pytest.fixture()
def socketio_client(client: FlaskTestClient) -> SocketIOTestClient:  # noqa: WPS442
    return SocketIOTestClient(client)
