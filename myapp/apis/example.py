import json
from flask import jsonify, make_response, Blueprint
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user
from werkzeug.exceptions import abort

from myapp.db import get_db

post = Blueprint("post", __name__)
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}
api = Namespace("post", description="Post API", authorizations=authorizations)

post_model = api.model(
    "Post",
    {
        "parent_id": fields.Integer(nullable=True, default=None, description="optional: parent post id"),
        "title": fields.String(required=True, description="The title of the post"),
        "body": fields.String(required=True, description="The body of the post"),
    },
)


@api.route("/")
class Post(Resource):
    @api.doc(description="Get list of all parent posts")
    def get(self):
        db = get_db()
        posts = db.execute(
            "Select p.id, title, body, created, author_id, parent_id, username"
            " From post p Join user u On p.author_id = u.id"
            " Where p.parent_id is Null"
            " Order By created Desc"
        ).fetchall()

        result = json.dumps([dict(row) for row in posts], indent=2, default=str)
        return make_response(result, 200)

    @api.doc(
        description="Create new post for user",
        responses={500: "Internal Server Error", 201: "Post successfully created"},
        security="Bearer",
    )
    @api.expect(post_model, Validate=True)
    @jwt_required()
    def post(self):
        parent_id = None
        if "parent_id" in api.payload:
            parent_id = api.payload["parent_id"]
        authorId = current_user["id"]

        db = get_db()
        try:
            db.execute(
                "Insert Into post (title, body, author_id, parent_id) Values(?, ?, ?, ?)",
                (api.payload["title"], api.payload["body"], authorId, parent_id),
            )
            db.commit()
        except db.DatabaseError as err:
            # log the err
            return make_response(jsonify(msg="Internal Server Error"), 500)

        return make_response(jsonify(msg="Post successfully created."), 201)


@api.route("/<id>")
@api.doc(params={"id": "Id the post"}, security="Bearer")
class PostResource(Resource):
    @jwt_required()
    def get(self, id):
        db = get_db()
        post = db.execute(
            "Select p.id, title, body, created, author_id, parent_id, username"
            " From post p Join user u On p.author_id = u.id"
            " Where p.id = ?",
            (id,),
        ).fetchone()

        return make_response(jsonify(dict(post)), 200)

    @api.expect(post_model)
    @jwt_required()
    def put(self, id):
        get_post(id)
        userId = current_user["id"]
        title = api.payload["title"]
        body = api.payload["body"]
        try:
            db = get_db()
            db.execute(
                "Update post" " Set title = ?, body = ?" " Where id = ? and author_id = ?",
                (
                    title,
                    body,
                    id,
                    userId,
                ),
            )
            db.commit()
        except db.DatabaseError as err:
            # log err somehwere
            return make_response(jsonify(msg="Internal Server Error."), 500)

        return make_response(jsonify(msg="Post successfully updated."), 204)

    @jwt_required()
    def delete(self, id):
        get_post(id)
        userId = current_user["id"]
        db = get_db()
        try:
            db.execute("Delete From post Where id = ? and author_id = ?", (id, userId))
            db.commit()
        except db.DatabaseError as err:
            # todo: log err
            return make_response(jsonify(msg="Internal Server Error"), 500)
        return "", 204


def get_post(id):
    authorId = current_user["id"]
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ? and p.author_id = ?",
            (id, authorId),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    return post
