from flask import current_app
from flask_fullstack import ResourceController
from flask_jwt_extended import get_jwt
from flask_restx import Resource
from flask_restx.reqparse import RequestParser

from common import User, BlockedToken, TEST_USERNAME1

controller = ResourceController("reglog", path="/")

auth_parser: RequestParser = RequestParser()
auth_parser.add_argument("username", type=str, required=True)
auth_parser.add_argument("password", type=str, required=True)


@controller.route("/sign-up/")
class Registration(Resource):
    @controller.doc_abort("200 ", "Username already in use")
    @controller.argument_parser(auth_parser)
    @controller.marshal_with_authorization(User.MainData)
    def post(self, username: str, password: str):
        if User.find_by_username(username) is not None:
            return "Username already in use"

        user = User.create(username, password)
        return user, user


@controller.route("/sign-in/")
class Authorization(Resource):
    @controller.doc_abort("200 ", "User doesn't exist")
    @controller.doc_abort(" 200", "Wrong password")
    @controller.argument_parser(auth_parser)
    @controller.marshal_with_authorization(User.MainData)
    def post(self, username: str, password: str):
        if (user := User.find_by_username(username)) is None:
            return "User doesn't exist"

        if User.verify_hash(password, user.password):
            return user, user
        return "Wrong password"


@controller.route("/home/")
class HomeData(Resource):
    @controller.jwt_authorizer(User)
    @controller.marshal_with(User.MainData)
    def get(self, user: User):
        return user


@controller.route("/go/")
class Test(Resource):
    @controller.marshal_with_authorization(User.MainData)
    def get(self):
        """Localhost-only endpoint for logging in from the docs"""
        if not current_app.debug:
            return {"a": False}

        user = User.find_by_username(TEST_USERNAME1)
        return user, user


@controller.route("/sign-out/")
class Logout(Resource):
    @controller.jwt_authorizer(User, check_only=True)
    @controller.removes_authorization()
    def post(self):
        BlockedToken.create(jti=get_jwt()["jti"])
        return True
