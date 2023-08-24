from flask_fullstack import ResourceController, EventController
from flask_restx import Resource
from flask_restx.reqparse import RequestParser

from common import Sign, User
from common.game_db import MoveGame

controller = ResourceController("game", path="/game")
event_controller = EventController()

result_game_parser: RequestParser = RequestParser()
result_game_parser.add_argument("room_name", type=str, required=True)
result_game_parser.add_argument("game_number", type=int, required=True)
result_game_parser.add_argument("user_id", type=int, required=True)


@controller.route('/move')
class Move(Resource):

    @controller.jwt_authorizer(User)
    @controller.marshal_with(Sign.BaseModel)
    def get(self):
        return Sign.get_all()


@controller.route('/result')
class ResultGame(Resource):

    @controller.jwt_authorizer(User)
    @controller.argument_parser(result_game_parser)
    @controller.marshal_with(MoveGame.BaseModel)
    def get(self, room_name: str, user_id: int, game_number: int):
        return MoveGame.find_winner(room_name=room_name, user_id=user_id, game_number=game_number)
