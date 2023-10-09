import pytest
from flask_fullstack import FlaskTestClient, SocketIOTestClient
from pydantic import constr
from werkzeug.test import TestResponse

from common.constants import TEST_USERNAME, TEST_PASSWORD
from main import app

app.test_client_class = FlaskTestClient


@pytest.fixture(scope="session", autouse=True)
def application_context() -> None:
    with app.app_context():
        yield


@pytest.fixture()
def base_client():
    app.debug = True
    with app.test_client() as client:
        yield client


def login(username: str, password: str) -> FlaskTestClient:
    client: FlaskTestClient
    with app.test_client() as client:
        response: TestResponse = client.post(
            "/sign-in/",
            data={"username": username, "password": password},
            expected_headers={"Set-Cookie": constr(pattern="access_token_cookie=.*")},
            get_json=False,
        )
        client.set_cookie(
            "test",
            "access_token_cookie",
            response.headers["Set-Cookie"].partition("=")[1],
        )
    return client


@pytest.fixture(scope="session")
def client() -> FlaskTestClient:
    return login(TEST_USERNAME, TEST_PASSWORD)


@pytest.fixture(scope="session")
def socketio_client(client: FlaskTestClient) -> SocketIOTestClient:  # noqa: WPS442
    return SocketIOTestClient(client)
