from __future__ import annotations

from flask import session
from flask_restx import Resource
from flask_fullstack import ResourceController
from flask_restx.reqparse import RequestParser

from common import TaskTodo as Task, User

controller = ResourceController(name="tasks", path="/")

task_parser: RequestParser = RequestParser()
task_parser.add_argument("name", type=str)
task_parser.add_argument("description", type=str)
task_parser.add_argument("start_task", type=str)
task_parser.add_argument("end_task", type=str)
task_parser.add_argument("category_id", type=int)


@controller.route("/list_tasks/")
class TodoListTasks(Resource):
    @controller.jwt_authorizer(User, check_only=True)
    @controller.marshal_list_with(Task.IndexModel)
    def get(self):
        if bool(Task.get_all(session['user_id'])) is False:
            return controller.abort(404, "list todo tasks empty")
        return Task.get_all(session['user_id'])


@controller.route("/detail_task/<string:task_name>")
class TodoDetailTask(Resource):
    error_message = "task todo not found task_name incorrect"

    @controller.jwt_authorizer(User, check_only=True)
    @controller.marshal_with(Task.IndexModel)
    def get(self, task_name: str) -> Task:
        if not (task := Task.find_first_by_kwargs(name=task_name, user_id=session['user_id'])) is None:
            return task
        controller.abort(404, self.error_message)
