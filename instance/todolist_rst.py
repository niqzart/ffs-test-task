from datetime import datetime

from flask_fullstack import RequestParser, ResourceController
from flask_restx import Resource

from common import User

from .todolist_db import Task

controller = ResourceController("TODO-LIST", path="/")


@controller.route("/to-do/")
class Todo(Resource):
    parser: RequestParser = RequestParser()
    parser.add_argument("title", type=str, required=True)
    parser.add_argument("category", type=str, required=True)
    parser.add_argument("date_time", type=str, required=True)
    parser.add_argument("duration", type=int, required=True)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(parser)
    @controller.marshal_with(Task.BaseModel)
    def post(
        self, user: User, title: str, category: str, date_time: str, duration: int
    ):
        task = Task.create(
            title=title,
            category=category,
            date_time=datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%f"),  # 2023-06-29T08:15:27.243860
            duration=duration,
            creator_id=user.id,
        )
        return task

    put_parser: RequestParser = RequestParser()
    put_parser.add_argument("task_id", type=int, required=True)
    put_parser.add_argument("title", type=str)
    put_parser.add_argument("category", type=str)
    put_parser.add_argument("date_time", type=str)
    put_parser.add_argument("duration", type=int)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(put_parser)
    @controller.marshal_with(Task.IndexModel)
    def put(
        self,
        task_id: int,
        user: User,
        title: str,
        category: str,
        date_time: str,
        duration: int,
    ):
        task = Task.find_by_id(entry_id=task_id)
        checks = [
            task.creator_id == user.id,
        ]
        if not any(checks):
            controller.abort(403, "Permission Denied")

        if title is not None:
            task.title = title
        if category is not None:
            task.category = category
        if date_time is not None:
            task.date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%f")
        if duration is not None:
            task.duration = duration

        if (
            title is not None
            or category is not None
            or date_time is not None
            or duration is not None
        ):
            task.changed = datetime.utcnow()

        return task

    delete_parser: RequestParser = RequestParser()
    delete_parser.add_argument("task_id", type=int, required=True)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(delete_parser)
    def delete(self, user: User, task_id: int):
        task = Task.find_by_id(entry_id=task_id)
        checks = [
            task.creator_id == user.id,
        ]
        if not any(checks):
            controller.abort(403, "Permission Denied")

        task.delete()

    @controller.jwt_authorizer(User)
    @controller.marshal_list_with(Task.BaseModel)
    def get(self, user: User):
        return Task.find_all_tasks_by_creator_id(entry_id=user.id)
