from flask_restx import Resource
from flask_fullstack import ResourceController
from flask_restx.reqparse import RequestParser

from . import Shapes, GameActPerUser
from common import User


controller = ResourceController(name="game", path='/')


game_parser = RequestParser()
game_parser.add_argument("game_id", type=int)
game_parser.add_argument("user_id", type=int)


@controller.route("/shapes/")
class Shape(Resource):

    @controller.jwt_authorizer(User)
    def get(self):
        return Shapes.list()


@controller.route("/game_results/")
class GameResults(Resource):

    @controller.jwt_authorizer(User)
    @controller.argument_parser(game_parser)
    def get(self, game_id: int, user_id: int):
        game = GameActPerUser.find_by_game_and_user_ids(
            game_id=game_id,
            user_id=user_id
        )
        return game.result
