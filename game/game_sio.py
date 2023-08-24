import random
import string

from flask_fullstack import EventController, EventSpace, DuplexEvent
from flask_socketio import join_room, close_room
from pydantic import BaseModel

from common import User, db
from common.game_db import MoveGame, Sign

controller = EventController()


@controller.route()
class RoomEventSpace(EventSpace):

    @classmethod
    def get_room_name(cls):
        """
        Создание название комнаты
        :return:
        """
        letters_and_digits = string.ascii_letters + string.digits
        room_name = ''.join(random.sample(letters_and_digits, 10))
        return room_name

    class RoomModel(BaseModel):
        room_name: str

    @controller.argument_parser(User.MainData)
    @controller.marshal_ack(RoomModel)
    def create_game(self):
        """
        Создание комнаты для игры
        """
        room_name = self.get_room_name()
        join_room(room_name)

        return room_name

    @controller.argument_parser(RoomModel)
    @controller.force_ack()
    def join_game(self, room_name: str):
        """
        Вход в комнату для игры
        :param room_name:
        :return:
        """
        join_room(room_name)

    @controller.argument_parser(RoomModel)
    @controller.force_ack()
    def leave_game(self, room_name: str):
        """
        Выход из комнаты для игры
        :param room_name:
        :return:
        """
        close_room(room_name)

    class GameModel(BaseModel, MoveGame.CreateBaseModel):

        pass

    def save_result(self, move_game_1: MoveGame, move_game_2: MoveGame):
        """
        Сохраняет итоги игры
        :param move_game_1: ход противника
        :param move_game_2: ход текущего игрока
        """
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
        """
        Сохраняет ход игрока. Если он сходил последним, то вызывает метод для расчета вычисления победителя и отправляет
         событие, чтобы вывести итоги игры
        """
        move_game_enemy = MoveGame.find_by_room_name(room_name)
        move_game_current_user = MoveGame.create(user.id, sign.id, room_name)
        db.session.commit()
        if move_game_enemy is not None:
            self.save_result(move_game_enemy, move_game_current_user)

            event.emit_convert(data={'result': 'ok', 'game_number': move_game_current_user.game_number},
                               room=room_name, include_self=True)
