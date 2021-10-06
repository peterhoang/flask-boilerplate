from myapp.db import get_db


def test_post_getall(client):
    response = client.get("/api/v1/post/")

    assert response.status_code == 200
    assert b"test title" in response.data


def test_post_create(client, app, headers):
    new_post = {"title": "new title", "body": "new body", "parent_id": 1}
    response = client.post("/api/v1/post/", headers=headers, content_type="application/json", json=new_post)
    assert response.status_code == 201

    with app.app_context():
        assert (
            get_db()
            .execute(
                "SELECT * FROM post WHERE title = 'new title' and body='new body'",
            )
            .fetchone()
            is not None
        )


def test_get_post_by_id(client, headers):
    response = client.get("/api/v1/post/1", headers=headers)
    json_data = response.get_json()
    assert response.status_code == 200
    assert b"test title" in response.data
    assert len(json_data) == 4
    assert json_data[0]["title"] == "test title"


def test_update_post(app, client, headers):
    changes = {"title": "changed title", "body": "changed body"}
    response = client.put("/api/v1/post/1", headers=headers, json=changes)
    assert response.status_code == 204
    with app.app_context():
        assert (
            get_db()
            .execute(
                "SELECT * FROM post WHERE title = 'changed title' and body='changed body'",
            )
            .fetchone()
            is not None
        )


def test_update_not_found_post(client, headers):
    changes = {"title": "changed title", "body": "changed body"}
    response = client.put("/api/v1/post/99", headers=headers, json=changes)
    assert response.status_code == 404


def test_delete_post(app, client, headers):
    new_post = {"title": "new title", "body": "new body", "parent_id": 1}
    response = client.post("/api/v1/post/", headers=headers, content_type="application/json", json=new_post)
    assert response.status_code == 201

    with app.app_context():
        assert (
            get_db()
            .execute(
                "SELECT * FROM post WHERE title = 'new title' and body='new body'",
            )
            .fetchone()
            is not None
        )

    response = client.get("/api/v1/post/6", headers=headers)
    assert response.status_code == 200
    assert b"new title" in response.data

    response = client.delete("/api/v1/post/1", headers=headers)
    assert response.status_code == 204

    response = client.get("/api/v1/post/6", headers=headers)
    assert response.status_code == 404
    assert b"Not found." in response.data

    with app.app_context():
        rows = get_db().execute("Select * From Post").fetchall()
        assert len(rows) == 2


def test_filter_test(client):
    response = client.get("/api/v1/post/filter?lastdate=2021-01-21")
    assert response is not None
    assert response.status_code == 200

    json_data = response.get_json()
    assert len(json_data) == 4

    response = client.get("/api/v1/post/filter?lastdate=2021-01-21&limit=2")
    json_data = response.get_json()
    assert len(json_data) == 2

    response = client.get("/api/v1/post/filter?firstdate=2021-04-01")
    json_data = response.get_json()
    assert len(json_data) == 3
