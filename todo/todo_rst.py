from flask_restx import Resource
from flask_fullstack import ResourceController
from flask_restx.reqparse import RequestParser

from common import CategoryTodo, User

controller = ResourceController("todo", path='/todo')

todo_category_parser = RequestParser()
todo_category_parser.add_argument("name", type=str)


@controller.route("/category/")
class CreateTodoCategory(Resource):
    @controller.doc_abort(205, "Category already exist")
    @controller.jwt_authorizer(User, check_only=True)
    @controller.argument_parser(todo_category_parser)
    @controller.marshal_with(CategoryTodo.MainData)
    def post(self, name):
        if (cat := CategoryTodo.find_first_by_kwargs(name=name)) is None:
            return CategoryTodo.create(name=name), 201
        return cat, 205
