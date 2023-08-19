from flask_fullstack import ResourceController, EventController, EventSpace
from flask_socketio import join_room, leave_room, send
from flask_restx import Resource
from flask_restx.reqparse import RequestParser
from pydantic import BaseModel

from common import User

controller = ResourceController("game", path="/game")
event_controller = EventController()

room_parser: RequestParser = RequestParser()
room_parser.add_argument("username", type=str, required=True)
room_parser.add_argument("room", type=int, required=True)


@controller.route("/")
class Game(Resource):

    # @controller.doc_abort("200 ", "User has left the room.")
    @controller.argument_parser(room_parser)
    @controller.marshal_with(User.MainData)
    def get(self, data: dict):
        return {'create_room': 'Create_room', 'join_room': 'Join room'}



# @controller.route('/selection')
# class Selection(Resource):

#     @controller.argument_parser(room_parser)
#     @controller.marshal_with(User.MainData)