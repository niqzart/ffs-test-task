from __future__ import annotations

from flask import session
from flask_restx import Resource
from flask_fullstack import ResourceController
from flask_restx.reqparse import RequestParser
from datetime import datetime

from common import TaskTodo as Task, User

controller = ResourceController(name="tasks", path="/")

task_parser: RequestParser = RequestParser()
task_parser.add_argument("name", type=str)
task_parser.add_argument("target", type=str)
task_parser.add_argument("start_task", type=str)
task_parser.add_argument("end_task", type=str)
task_parser.add_argument("category_id", type=int)


def get_datetime(date_time: str) -> datetime:
    return datetime(*[int(i) for i in date_time.split()])


@controller.route("/list_tasks/")
class TodoListTasks(Resource):
    @controller.jwt_authorizer(User, check_only=True)
    @controller.marshal_list_with(Task.MainData)
    def get(self):
        if bool(Task.get_all(session['user_id'])) is False:
            return controller.abort(404, "list todo tasks empty")
        return Task.get_all(session['user_id'])


@controller.route("/create_task/")
class TodoCreateTask(Resource):
    @controller.jwt_authorizer(User, check_only=True)
    @controller.argument_parser(task_parser)
    @controller.marshal_with(Task.MainData)
    def post(self, **kwargs):
        if Task.find_first_by_kwargs(name=kwargs["name"], user_id=session['user_id']) is None:
            return Task.create(
                name=kwargs['name'],
                target=kwargs['target'],
                start_task=get_datetime(kwargs['start_task']),
                end_task=get_datetime(kwargs['end_task']),
                category_id=kwargs['category_id'],
                user_id=session['user_id']
            )
        controller.abort(404, "task alredy exist")


@controller.route("/detail_task/<string:task_name>")
class TodoDetailTask(Resource):
    error_message = "task todo not found task_name incorrect"
    success_message = "task was deleted"

    @controller.jwt_authorizer(User, check_only=True)
    @controller.marshal_with(Task.MainData)
    def get(self, task_name: str) -> Task:
        if not (task := Task.find_first_by_kwargs(name=task_name, user_id=session['user_id'])) is None:
            return task
        controller.abort(404, self.error_message)

    @controller.jwt_authorizer(User, check_only=True)
    @controller.argument_parser(task_parser)
    @controller.marshal_with(Task.MainData)
    def patch(self, **kwargs) -> Task:
        if (task := Task.find_first_by_kwargs(name=kwargs['task_name'], user_id=session['user_id'])) is None:
            controller.abort(404, self.error_message)
        return Task.change_values(task, **kwargs)

    @controller.jwt_authorizer(User, check_only=True)
    def delete(self, task_name: str):
        if (task := Task.find_first_by_kwargs(name=task_name, user_id=session['user_id'])) is None:
            controller.abort(404, self.error_message)
        task.delete()
        return "task was deleted"

