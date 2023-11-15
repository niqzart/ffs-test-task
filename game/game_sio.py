from flask_fullstack import EventController, EventSpace, DuplexEvent
from flask_socketio import join_room, leave_room

from common import User
from . import Game, GameModel


controller = EventController()


@controller.route()
class RoomEventSpace(EventSpace):

    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    @controller.mark_duplex(Game.IdModel, use_event=True)
    @controller.marshal_ack(Game.IdModel)
    def start(self, event: DuplexEvent, user: User) -> str:
        game = Game.create()
        join_room(game.room_number)
        event.emit_convert(
            game,
            data={'room_number': game.room_number},
            room=game.room_number,
            include_self=True)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    def join(self, user: User, room_number: str):
        join_room(room_number)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    def leave(self, user: User, room_number: str):
        leave_room(room_number)

    def get_results(
        self,
        game_id: int,
        user_id: int,
        user_option: str,
        enemy_id: int,
        enemy_option: str
    ):
        game_user = GameModel.find_by_game_and_user_ids(game_id, user_id)
        game_enemy = GameModel.find_by_game_and_user_ids(game_id, enemy_id)

        if user_option == enemy_option:
            game_user.result, game_enemy.result = 'TIE', 'TIE'
        elif (
            user_option.lower() == 'scissors' and enemy_option.lower() == 'rock'
        ) or (
            user_option.lower() == 'paper' and enemy_option.lower() == 'scissors'
        ) or (user_option.lower() == 'rock' and enemy_option.lower() == 'paper'):
            game_user.result, game_enemy.result = 'LOSE', 'WIN'
        else:
            game_user.result, game_enemy.result = 'WIN', 'LOSE'

    @controller.jwt_authorizer(User)
    @controller.argument_parser()
    @controller.mark_duplex(GameModel.IdModel, use_event=True)
    @controller.marshal_ack(GameModel.IdModel)
    def make_shape_choice(
        self,
        event: DuplexEvent,
        game_id: int,
        room_code: str,
        user: User,
        option: str
    ):
        game = GameModel.find_by_game_and_user_ids(game_id, user.id)
        game.option = option
        enemy = GameModel.find_enemy(game_id, user.id)
        enemys_option = enemy.option
        if enemys_option:
            self.get_results(game_id, user.id, option, enemy.id, enemys_option)
            return event.emit_convert(
                game,
                room=room_code,
                include_self=True
            )