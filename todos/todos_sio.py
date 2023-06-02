from __future__ import annotations

from flask_fullstack import EventController, EventSpace, DuplexEvent

from common import User
from todos.todos_db import Todo
from todos.utils import parse_date

controller: EventController = EventController()


@controller.route()
class TodosListEventSpace(EventSpace):
    @controller.jwt_authorizer(User)
    @controller.argument_parser(Todo.BaseModel)
    @controller.mark_duplex(Todo.BaseModel, use_event=True)
    @controller.marshal_ack(Todo.IndexModel)
    def create_todo(
            self,
            event: DuplexEvent,
            user: User,
            task: str,
            category: str,
            date: str,
            duration: int,
    ) -> Todo | None:
        todo = Todo.create(
            task=task,
            category=category,
            date=parse_date(date),
            duration=duration,
            user_id=user.id,
        )

        event.emit_convert(todo)
        return todo

    @controller.doc_abort(404, "TODO Not Found")
    @controller.doc_abort(403, "Permission Denied")
    @controller.jwt_authorizer(User)
    @controller.argument_parser(Todo.IndexModel)
    @controller.mark_duplex(Todo.IndexModel, use_event=True)
    @controller.marshal_ack(Todo.IndexModel)
    def update_todo(
            self,
            event: DuplexEvent,
            user: User,
            todo_id: int,
            task: str,
            category: str,
            date: str,
            duration: int,
    ) -> Todo | None:
        if (todo := Todo.get_by_id(todo_id=todo_id, user_id=user.id)) is None:
            controller.abort(404, "TODO Not Found")
        elif todo.user_id != user.id:
            controller.abort(403, "Permission Denied")

        todo.task = task or todo.task
        todo.category = category or todo.category
        todo.date = date or todo.date
        todo.duration = duration or todo.duration

        event.emit_convert(todo)
        return todo

    @controller.doc_abort(404, "TODO Not Found")
    @controller.doc_abort(403, "Permission Denied")
    @controller.jwt_authorizer(User)
    @controller.argument_parser(Todo.DeleteModel)
    @controller.mark_duplex(Todo.DeleteModel, use_event=True)
    @controller.force_ack()
    def delete_todo(
            self,
            event: DuplexEvent,
            user: User,
            todo_id: int,
    ):
        if (todo := Todo.get_by_id(todo_id=todo_id, user_id=user.id)) is None:
            controller.abort(404, "TODO Not Found")
        elif todo.user_id != user.id:
            controller.abort(403, "Permission Denied")

        todo.delete()
        event.emit_convert()
