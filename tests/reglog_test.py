from flask_fullstack import FlaskTestClient
from pydantic import constr

from common import TEST_USERNAME, TEST_PASSWORD

TEST_CREDENTIALS = {"username": TEST_USERNAME, "password": TEST_PASSWORD}


def test_login(base_client: FlaskTestClient):
    base_client.post(
        "/sign-in/",
        json=TEST_CREDENTIALS,
        expected_json={"id": int, "username": TEST_USERNAME},
        expected_headers={"Set-Cookie": constr(regex="access_token_cookie=.*")},
    )
    base_client.post("/sign-out/")
