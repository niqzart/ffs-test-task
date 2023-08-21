from flask_fullstack import EventController, EventSpace, ClientEvent, DuplexEvent
from flask_socketio import join_room, leave_room, send, emit
from flask_restx import Resource
from pydantic import BaseModel

from common import User, db
from common.game_db import MoveGame

controller = EventController()


@controller.route()
class RoomEventSpace(EventSpace):

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

    class GameModel(BaseModel, MoveGame.CreateBaseModel):

        pass

    @controller.argument_parser(GameModel)
    @controller.mark_duplex(MoveGame.CreateBaseModel)
    @controller.force_ack()
    def get_users_choice(
            self,
            event: ClientEvent,
            user_id: int,
            sign_id: int,
            room_name: str,
            game: GameModel
    ):
        move_game_user = MoveGame.find_by_room_name(room_name)
        if move_game_user is None:
            MoveGame.create(user_id, sign_id, room_name)
            db.session.commit()
        else:
             # если данный пользователь последний выбрал знак, то подводяться итоги и вывводится результат
             pass


