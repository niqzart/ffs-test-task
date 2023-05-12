from datetime import datetime

from flask_fullstack import DuplexEvent, EventSpace
from pydantic import BaseModel

from common import EventController, User

from .todolist_db import Task

controller = EventController()


@controller.route()
class TodoEventSpace(EventSpace):
    @controller.argument_parser(Task.IndexModel)
    @controller.mark_duplex(Task.IndexModel, use_event=True)
    @controller.jwt_authorizer(User)
    @controller.marshal_ack(Task.IndexModel)
    def create_task(
        self,
        event: DuplexEvent,
        title: str,
        category: str,
        date_time: str,
        duration: int,
    ):
        task = Task.create(
            title=title,
            category=category,
            date_time=datetime.strptime(
                date_time, "%Y-%m-%dT%H:%M:%S.%f"
            ),
            duration=duration,
            creator_id=1,
        )
        event.emit_convert(task)
        return task

    class TaskIdModel(BaseModel):
        task_id: int

    @controller.argument_parser(TaskIdModel)
    @controller.mark_duplex(use_event=True)
    @controller.jwt_authorizer(User)
    @controller.database_searcher(Task)
    @controller.force_ack()
    def delete_task(
        self,
        event: DuplexEvent,
        user: User,
        task: Task
    ):
        checks = [
            task.creator_id == user.id,
        ]
        if not any(checks):
            controller.abort(403, "Permission Denied")
        task.delete()
        event.emit_convert(task)
