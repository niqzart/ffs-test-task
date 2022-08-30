from flask import current_app
from flask_jwt_extended import get_jwt
from flask_restx import Resource
from flask_restx.reqparse import RequestParser

from __lib__.flask_fullstack import ResourceController
from common import sessionmaker, User, BlockedToken, TEST_USERNAME

controller = ResourceController("reglog", sessionmaker=sessionmaker, path="/")

auth_parser: RequestParser = RequestParser()
auth_parser.add_argument("username", type=str, required=True)
auth_parser.add_argument("password", type=str, required=True)


@controller.route("/sign-up/")
class Registration(Resource):
    @controller.doc_abort("200 ", "Username already in use")
    @controller.with_begin
    @controller.argument_parser(auth_parser)
    @controller.marshal_with_authorization(User.MainData)
    def post(self, session, username: str, password: str):
        if User.find_by_username(session, username) is not None:
            return "Username already in use"

        user = User.create(session, username, password)
        return user, user


@controller.route("/sign-in/")
class Authorization(Resource):
    @controller.doc_abort("200 ", "User doesn't exist")
    @controller.doc_abort(" 200", "Wrong password")
    @controller.with_begin
    @controller.argument_parser(auth_parser)
    @controller.marshal_with_authorization(User.MainData)
    def post(self, session, username: str, password: str):
        if (user := User.find_by_username(session, username)) is None:
            return "User doesn't exist"

        if User.verify_hash(password, user.password):
            return user, user
        return "Wrong password"


@controller.route("/home/")
class HomeData(Resource):
    @controller.jwt_authorizer(User, use_session=False)
    @controller.marshal_with(User.MainData)
    def get(self, user: User):
        return user


@controller.route("/go/")
class Test(Resource):
    @controller.with_begin
    @controller.marshal_with_authorization(User.MainData)
    def get(self, session):
        """ Localhost-only endpoint for logging in from the docs """
        if not current_app.debug:
            return {"a": False}

        user = User.find_by_username(session, TEST_USERNAME)
        return user, user


@controller.route("/sign-out/")
class Logout(Resource):
    @controller.jwt_authorizer(User, check_only=True)
    @controller.removes_authorization()
    def post(self, session):
        BlockedToken.create(session, jti=get_jwt()["jti"])
        return True
