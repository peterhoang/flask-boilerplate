import os
from flask import Flask, Blueprint
from flask_restx import Api
from flask_jwt_extended import JWTManager
from . import db


def user_identity_lookup(user):
    return user["id"]


def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    userDto = db.get_db().execute("Select * From user Where id = ?", (identity,)).fetchone()
    userObj = None
    if userDto is not None:
        userDict = dict(userDto)
        userObj = {"id": userDict["id"], "username": userDict["username"]}
    return userObj


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "myapp.sqlite"),
    )
    api = Api(
        app,
        version="1.0",
        title="MyApp API",
        description="A simple Rest API for MyApp",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    # load blueprints and myapp namespaces
    from .apis.auth import auth, api as auth_ns1

    blueprint = Blueprint("api", __name__)
    api = Api(blueprint)
    app.register_blueprint(blueprint, url_prefix="/api")
    app.register_blueprint(auth)

    api.add_namespace(auth_ns1, path="/v1/auth")

    # load JWT stuff
    jwt = JWTManager(app)

    jwt.user_identity_loader(user_identity_lookup)
    jwt.user_lookup_loader(user_lookup_callback)

    return app
