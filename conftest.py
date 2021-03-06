import os
import tempfile
import pytest
import json
from myapp import create_app
from myapp.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "tests/data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/api/v1/auth/login", content_type="application/json", json={"username": username, "password": password}
        )


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def headers(auth):
    response = auth.login()
    token = json.loads(response.data)
    return {"Authorization": "Bearer {}".format(token["access_token"])}
