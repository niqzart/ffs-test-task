from flask_restx import Resource
from flask_fullstack import ResourceController
from flask_restx.reqparse import RequestParser

from common import CategoryTodo as Category, User

controller = ResourceController("category", path='/category/')

category_parser = RequestParser()
category_parser.add_argument("name", type=str)


@controller.route("/")
class CreateTodoCategory(Resource):
    @controller.doc_abort(205, "Category already exist")
    @controller.jwt_authorizer(User, check_only=True)
    @controller.argument_parser(category_parser)
    @controller.marshal_with(Category.MainData)
    def post(self, name: str):
        if (cat := Category.find_first_by_kwargs(name=name)) is None:
            return Category.create(name=name), 201
        return cat, 205
