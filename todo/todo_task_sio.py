from flask_fullstack import DuplexEvent, EventSpace, EventController
from flask_socketio import join_room, leave_room
from pydantic import BaseModel
from common import User, TaskTodo, db
from datetime import datetime

controller: EventController = EventController()


def get_datetime(date_time: str) -> datetime:
    return datetime(*[int(i) for i in date_time.split()])


@controller.route()
class TaskEventSpace(EventSpace):

    @classmethod
    def room_name(cls, user_id: int) -> str:
        return f"cat-{user_id}"

    class UserIdModel(BaseModel):
        user_id: int

    @controller.argument_parser(UserIdModel)
    @controller.force_ack()
    def open_room(self, user: User.id) -> None:
        join_room(self.room_name(user.id))

    @controller.argument_parser(UserIdModel)
    @controller.force_ack()
    def close_room(self, user: User) -> None:
        leave_room(self.room_name(user.id))

    class CreateModel(TaskTodo.CreationBaseModel, UserIdModel):
        pass

    @controller.argument_parser(CreateModel)
    @controller.mark_duplex(TaskTodo.IndexModel, use_event=True)
    @controller.jwt_authorizer(User)
    @controller.marshal_ack(TaskTodo.BaseModel)
    def new_task(
            self,
            event: DuplexEvent,
            name: str,
            description: str,
            start_task: str,
            end_task: str,
            user: User
    ):
        if TaskTodo.find_first_by_kwargs(name=name, user_id=user.id) is None:
            task = TaskTodo.create(
                name=name,
                description=description,
                start_task=get_datetime(start_task),
                end_task=get_datetime(end_task),
                user=user.id
            )
            event.emit_convert(task, self.room_name(user.id))
        controller.abort(404, "task alredy exist")

    class UpdateModel(TaskTodo.CreationBaseModel, UserIdModel):
        task_id: int

    @controller.argument_parser(UpdateModel)
    @controller.mark_duplex(TaskTodo.IndexModel)
    @controller.jwt_authorizer(User)
    @controller.marshal_ack(TaskTodo.IndexModel)
    def update_task(
            self,
            event: DuplexEvent,
            name: str,
            description: str,
            start_task: str,
            end_task: str,
            user: User
    ):
        if (task := TaskTodo.find_first_by_kwargs(name=name, user_id=user.id)) is None:
            controller.abort(404, self.error_message)

        changed_task = TaskTodo.change_values(
            task, **{"task_name": name,
                     "description": description,
                     "start_task": start_task,
                     "end_task": end_task
                     }
        )
        db.session.commit()
        event.emit_convert(changed_task, self.room_name(user.id))

    class DeleteModel(UserIdModel):
        task_id: int

    @controller.argument_parser(DeleteModel)
    @controller.mark_duplex(DeleteModel, use_event=True)
    @controller.jwt_authorizer(User)
    @controller.database_searcher(TaskTodo)
    @controller.force_ack()
    def delete_task(
            self,
            event: DuplexEvent,
            user: User,
            task_todo: TaskTodo
    ):
        task_todo.delete()
        db.session.commit()
        event.emit_convert(
            room=self.room_name(user.id),
            user_id=user.id,
            task_todo=task_todo.id
        )
