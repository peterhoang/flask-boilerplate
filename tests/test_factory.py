from myapp import create_app, user_lookup_callback, user_identity_lookup


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_user_lookup_callback(app):
    with app.app_context():
        result = user_lookup_callback(None, {"sub": 1})
        assert result is not None
        assert result["username"] == "test"

        result = user_lookup_callback(None, {"sub": -1})
        assert result is None


def test_user_identity_loockup(app):
    user = {"id": 1}
    with app.app_context():
        result = user_identity_lookup(user)
        assert result == 1
