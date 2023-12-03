from flask_restx import Resource
from flask_fullstack import ResourceController
from flask_restx.reqparse import RequestParser

from game.game_db import GameRounds, Game
from common import User

controller = ResourceController(name="game", path="/game/")

game_parser = RequestParser()
game_parser.add_argument("game_id", type=int, required=True)
game_parser.add_argument("user_id", type=int, required=True)

@controller.route("/all/")
class Games(Resource):
    """
    Фукнция для работы с играми
    """

    @controller.jwt_authorizer(User)
    @controller.marshal_with(Game.IdModel)
    def get_all(self, _):
        """
        Получить все игры
        """
        return Game.get()

@controller.route("/results/")
class ResultGame(Resource):
    """
    Функция для получения результатов игр
    """

    @controller.jwt_authorizer(User)
    @controller.argument_parser(game_parser)
    @controller.marshal_with(Game.IdModel)
    def get_result_game(self, _, game_id: int, user_id: int):
        """
        Получить результаты игры
        """
        game = GameRounds.find_by_game_and_user_ids(
            game_id=game_id,
            user_id=user_id
        )
        return game.result

@controller.route("/all-detailed/")
class UserAllGames(Resource):
    """
    Функция для получения детальной информации о играх пользователя
    """

    @controller.jwt_authorizer(User)
    @controller.argument_parser(game_parser)
    @controller.marshal_with(Game.IdModel)
    def all_games(self, user: User):
        """
        Получить все игры пользователя
        """
        return GameRounds.get_user_all_game(user_id=user.id)
