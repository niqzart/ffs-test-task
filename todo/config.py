from flask_fullstack import EventController
from flask_socketio import join_room, leave_room
from pydantic import BaseModel
from common import User

controller: EventController = EventController()


class UserRoom:
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
