from __future__ import annotations

from datetime import datetime

from flask_restx import Resource
from flask_fullstack import ResourceController, RequestParser

from common import User
from todos.todos_db import Todo
from todos.utils import parse_date

controller: ResourceController = ResourceController("todos", path="/todos/")


@controller.route("/")
class TodosList(Resource):
    parser = RequestParser()
    parser.add_argument("task", type=str, required=True)
    parser.add_argument("category", type=str, required=True)
    parser.add_argument("date", type=parse_date, required=True)
    parser.add_argument("duration", type=int, required=True)

    get_parser = RequestParser()
    get_parser.add_argument("date", type=parse_date, required=False)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(get_parser)
    @controller.marshal_list_with(Todo.IndexModel)
    def get(self, user: User, date: datetime | None) -> list[Todo]:
        if date is not None:
            return Todo.find_by_date(date=date, user_id=user.id)
        return Todo.find_by_user_id(user.id)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(parser)
    @controller.marshal_with(Todo.IndexModel)
    def post(
            self,
            user: User,
            task: str,
            category: str,
            date: datetime,
            duration: int,
    ) -> Todo | None:
        return Todo.create(
            task=task,
            category=category,
            date=date,
            duration=duration,
            user_id=user.id,
        )


@controller.route("/<int:todo_id>/")
class Todos(Resource):
    parser = RequestParser()
    parser.add_argument("task", type=str, required=False)
    parser.add_argument("category", type=str, required=False)
    parser.add_argument("date", type=parse_date, required=False)
    parser.add_argument("duration", type=int, required=False)

    @controller.doc_abort(404, "TODO Not Found")
    @controller.doc_abort(403, "Permission Denied")
    @controller.jwt_authorizer(User)
    @controller.marshal_with(Todo.IndexModel)
    def get(self, user: User, todo_id: int) -> Todo:
        if (todo := Todo.get_by_id(user_id=user.id, todo_id=todo_id)) is None:
            controller.abort(404, "TODO Not Found")
        elif todo.user_id != user.id:
            controller.abort(403, "Permission Denied")
        return todo

    @controller.doc_abort(404, "TODO Not Found")
    @controller.doc_abort(403, "Permission Denied")
    @controller.jwt_authorizer(User)
    @controller.argument_parser(parser)
    @controller.marshal_with(Todo.IndexModel)
    def patch(
            self,
            user: User,
            todo_id: int,
            task: str | None,
            category: str | None,
            date: datetime | None,
            duration: str | None,
    ) -> Todo:
        if (todo := Todo.get_by_id(user_id=user.id, todo_id=todo_id)) is None:
            controller.abort(404, "TODO Not Found")
        elif todo.user_id != user.id:
            controller.abort(403, "Permission Denied")

        todo.task = task or todo.task
        todo.category = category or todo.category
        todo.date = date or todo.date
        todo.duration = duration or todo.duration
        return todo

    @controller.doc_abort(404, "TODO Not Found")
    @controller.doc_abort(403, "Permission Denied")
    @controller.jwt_authorizer(User)
    def delete(self, user: User, todo_id: int) -> tuple[dict, int]:
        if (todo := Todo.get_by_id(user_id=user.id, todo_id=todo_id)) is None:
            controller.abort(404, "TODO Not Found")
        elif todo.user_id != user.id:
            controller.abort(403, "Permission Denied")

        todo.delete()
        return {"message": "TODO successfully deleted"}, 200
