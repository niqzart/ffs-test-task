from __future__ import annotations

from flask import request, session
from flask_restx import Resource
from flask_fullstack import ResourceController
from flask_restx.reqparse import RequestParser
from datetime import datetime

from common import TaskTodo as Task, User, TaskTodo

controller = ResourceController(name="tasks", path="/tasks/")

task_parser = RequestParser()
task_parser.add_argument("name", type=str)
task_parser.add_argument("target", type=str)
task_parser.add_argument("start_task", type=str)
task_parser.add_argument("end_task", type=str)
task_parser.add_argument("category_id", type=int)


def get_datetime(date_time: str) -> datetime:
    return datetime(*[int(i) for i in date_time.split()])


@controller.route("/")
class TodoTasks(Resource):
    @controller.jwt_authorizer(User, check_only=True)
    @controller.argument_parser(task_parser)
    @controller.marshal_with(Task.MainData)
    def post(self, **kwargs):
        if (task := Task.find_first_by_kwargs(name=kwargs["name"])) is None:
            return Task.create(
                name=kwargs['name'],
                target=kwargs['target'],
                start_task=get_datetime(kwargs['start_task']),
                end_task=get_datetime(kwargs['end_task']),
                category_id=kwargs['category_id'],
                user_id=session['user_id']
            )
        return task, 205

    @controller.jwt_authorizer(User, check_only=True)
    @controller.marshal_list_with(Task.MainData)
    def get(self):
        return Task.get_all(), 200
