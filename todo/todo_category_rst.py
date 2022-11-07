from flask_restx import Resource
from flask_fullstack import ResourceController
from flask_restx.reqparse import RequestParser
from typing import Any

from common import CategoryTodo as Category, User

controller: ResourceController = ResourceController("category", path='/')
category_parser: RequestParser = RequestParser()
category_parser.add_argument("name", type=str)


@controller.route("/create_category/")
class CreateTodoCategory(Resource):
    @controller.jwt_authorizer(User, check_only=True)
    @controller.argument_parser(category_parser)
    @controller.marshal_with(Category.MainData)
    def post(self, name: str) -> Any:
        if Category.find_first_by_kwargs(name=name) is None:
            return Category.create(name=name), 201
        return controller.abort(404, "Category already exist")
