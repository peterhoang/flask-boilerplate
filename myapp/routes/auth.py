from flask import jsonify, make_response, Blueprint, request, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token

from myapp.db import get_db

auth = Blueprint("auth", __name__)
api = Namespace("auth", description="Authentiation API")

user_model = api.model(
    "User",
    {
        "username": fields.String(required=True, description="The username."),
        "password": fields.String(required=True, description="The password."),
    },
)


@api.route("/register")
@api.doc(description="Register for a new user.")
class Register(Resource):
    @api.doc(responses={400: "Validation Error", 201: "User successfully created"})
    @api.expect(user_model, validate=True)
    def post(self):
        username = api.payload["username"]
        password = api.payload["password"]

        try:
            db = get_db()
            db.execute(
                "Insert Into user (username, password) Values (?, ?)",
                (
                    username,
                    generate_password_hash(password),
                ),
            )
            db.commit()
        except db.IntegrityError:
            current_app.logger.error(f"User {username} is already registered.")
            return {"msg": f"User {username} is already registered."}, 400

        return make_response(jsonify({"msg": "user successfully registered."}), 201)


@api.route("/login")
@api.doc(description="Login a user.")
class Login(Resource):
    @api.doc(responses={401: "Unauthorized"})
    @api.expect(user_model, Validate=True)
    def post(self):
        username = api.payload["username"]
        password = api.payload["password"]
        userDto = get_db().execute("Select * From user Where username = ?", (username,)).fetchone()

        if userDto is None or not check_password_hash(userDto["password"], password):
            current_app.logger.warning(f"Incorrect login for {username} from: {request.remote_addr}")
            return {"msg": "Incorrect username or password."}, 401

        userDict = dict(userDto)
        userObj = {"id": userDict["id"], "username": userDict["username"]}
        access_token = create_access_token(identity=userObj)
        return jsonify(access_token=access_token)
