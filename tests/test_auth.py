from myapp.db import get_db


def test_register(client, app):
    response = client.post(
        "/api/v1/auth/register", content_type="application/json", json={"username": "a", "password": "a"}
    )
    assert b"user successfully registered." in response.data

    with app.app_context():
        assert (
            get_db()
            .execute(
                "SELECT * FROM user WHERE username = 'a'",
            )
            .fetchone()
            is not None
        )


def test_register_existing_user(client):
    response = client.post(
        "/api/v1/auth/register", content_type="application/json", json={"username": "test", "password": "test"}
    )
    assert response.status_code == 400
    assert b"User test is already registered." in response.data


def test_login(auth):
    response = auth.login()
    assert b"access_token" in response.data
    assert b"Incorrect username or password" not in response.data

    response = auth.login("baduser", "badpassword")
    assert b"Incorrect username or password" in response.data
