from flask_fullstack import EventController, EventSpace
from flask_socketio import join_room, leave_room, send, emit
from flask_restx import Resource
from pydantic import BaseModel

from common import User

controller = EventController()


@controller.route()
class Room(EventSpace):

    @classmethod
    def get_room_name(cls, user_id: int):
        return f"room_{user_id}"

    class RoomIdModel(BaseModel):
        room_id: int

    @controller.argument_parser(RoomIdModel)
    @controller.force_ack()
    def create_game(self, room: RoomIdModel):
        join_room(self.get_room_name(room.room_id))

    @controller.argument_parser(RoomIdModel)
    @controller.force_ack()
    def leave_game(self, room: RoomIdModel):
        leave_room(self.get_room_name(room.room_id))


