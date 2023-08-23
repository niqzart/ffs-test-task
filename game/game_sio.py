import random
import string

from flask_fullstack import EventController, EventSpace, ClientEvent, DuplexEvent
from flask_socketio import join_room, close_room
from flask_restx import Resource
from pydantic import BaseModel

from common import User, db
from common.game_db import MoveGame, Sign

controller = EventController()


@controller.route()
class RoomEventSpace(EventSpace):

    @classmethod
    def get_room_name(cls, user_id: int):
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, 10))
        return rand_string

    class RoomModel(BaseModel):
        room_name: str

    @controller.argument_parser(User.MainData)
    @controller.force_ack()
    def create_game(self, user: User):
        room_name = self.get_room_name(user.id)
        join_room(room_name)

        return room_name

    @controller.argument_parser(RoomModel)
    @controller.mark_duplex(Sign.BaseModel, use_event=True)
    @controller.marshal_ack(Sign.BaseModel)
    def join_game(
            self,
            event: DuplexEvent,
            room_name: str
    ):
        join_room(room_name)

        sign_list = Sign.get_all()
        event.emit_convert(data=sign_list, room=room_name, include_self=True)

    @controller.argument_parser(RoomModel)
    @controller.force_ack()
    def leave_game(self, room_name: str):
        close_room(room_name)

    class GameModel(BaseModel, MoveGame.CreateBaseModel):

        pass

    def get_result(cls, move_game_1: MoveGame, move_game_2: MoveGame):

        if move_game_1.sign.is_wins == move_game_2.sign.id:
            move_game_1.result = 'win'
            move_game_2.result = 'lose'

        elif move_game_1.sign.id == move_game_2.sign.id:
            move_game_1.result = 'tie'
            move_game_2.result = 'tie'

        else:
            move_game_1.result = 'lose'
            move_game_2.result = 'win'

        db.session.commit()

        return move_game_1, move_game_2

    @controller.argument_parser(GameModel)
    @controller.mark_duplex(MoveGame.CreateBaseModel, use_event=True)
    @controller.marshal_ack(MoveGame.CreateBaseModel)
    def create_move_game(
            self,
            event: DuplexEvent,
            user: User,
            sign: Sign,
            room_name: str,
    ):
        move_game_enemy = MoveGame.find_by_room_name(room_name)
        move_game_current_user = MoveGame.create(user.id, sign.id, room_name)
        db.session.commit()
        if move_game_enemy is not None:
            result_game_enemy, result_game_current_user = self.get_result(move_game_enemy, move_game_current_user)

            result = {
                f'user_{result_game_current_user.user_id}': result_game_current_user,
                f'user_{result_game_enemy}': result_game_enemy
            }

            event.emit_convert(data=result, room=room_name, include_self=True)
