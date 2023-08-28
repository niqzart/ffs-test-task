from flask_fullstack import EventController, EventSpace
from flask_socketio import join_room, leave_room
from common import User
from . import Game, GameActPerUser


controller = EventController()


@controller.route()
class RoomEventSpace(EventSpace):

    def start_new_game(self, user: User) -> str:
        game = Game.create(creator_id=user.id)
        join_room(game.room_code)
        return game.room_code

    def join_game(self, user: User, room_code: str):
        game = Game.find_by_room_code(room_code)
        game.joined_id = user.id
        join_room(room_code)

    def leave_game(self, user: User, room_code: str):
        leave_room(room_code)

    def get_results(
        self,
        game_id: int,
        user_id: int,
        user_shape: str,
        enemy_id: int,
        enemy_shape: str
    ):
        game_user = GameActPerUser.find_by_game_and_user_ids(game_id, user_id)
        game_enemy = GameActPerUser.find_by_game_and_user_ids(game_id, enemy_id)

        if user_shape == enemy_shape:
            game_user.result, game_enemy.result = 'TIE', 'TIE'
        elif (
            user_shape.lower() == 'scissors' and enemy_shape.lower() == 'rock'
        ) or (
            user_shape.lower() == 'paper' and enemy_shape.lower() == 'scissors'
        ) or (user_shape.lower() == 'rock' and enemy_shape.lower() == 'paper'):
            game_user.result, game_enemy.result = 'LOSE', 'WIN'
        else:
            game_user.result, game_enemy.result = 'WIN', 'LOSE'

    def make_shape_chiose(self, game_id: int, user: User, shape: str):
        game = GameActPerUser.find_by_game_and_user_ids(game_id, user.id)
        game.shape = shape
        enemy = GameActPerUser.get_enemy(game_id, user.id)
        enemys_shape = enemy.shape
        if enemys_shape:
            self.get_results(game_id, user.id, shape, enemy.id, enemys_shape)
