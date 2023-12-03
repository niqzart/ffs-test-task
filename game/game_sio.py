from flask_fullstack import EventController, EventSpace, DuplexEvent
from flask_socketio import join_room, leave_room

from common import User
from game.game_db import Game, GameRounds, GameResults, Options

controller = EventController()


@controller.route()
class RoomEventSpace(EventSpace):

    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    @controller.mark_duplex(Game.IdModel, use_event=True)
    @controller.marshal_ack(Game.IdModel)
    def start(
        self, 
        event: DuplexEvent, 
        _,
        game_id: int,
        room_number: str
    ) -> str:
        """Start a new game."""
        game = Game.create(game_id, room_number)
        join_room(game.room_number)
        event.emit_convert(
            game,
            data={'room_number': game.room_number},
            room=game.room_number
        )


    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    @controller.mark_duplex(Game.IdModel, use_event=True)
    @controller.marshal_ack(Game.IdModel)
    def join(self, _, game_id: str):
        """Join an existing game."""
        join_room(game_id)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    @controller.mark_duplex(Game.IdModel, use_event=True)
    @controller.marshal_ack(Game.IdModel)
    def leave(self, _, room_number: str):
        """Leave the current game."""
        leave_room(room_number)

    def get_results(
        self,
        game_id: int,
        user_id: int,
        user_option: str,
        enemy_id: int,
        enemy_option: str
    ):
        """Determine game results based on user and enemy choices."""
        game_user = GameRounds.find_by_game_and_user_ids(game_id, user_id)
        game_enemy = GameRounds.find_by_game_and_user_ids(game_id, enemy_id)

        results_dict = {
            (Options.ROCK, Options.SCISSORS): (GameResults.WIN, GameResults.LOSE),
            (Options.PAPER, Options.ROCK): (GameResults.WIN, GameResults.LOSE),
            (Options.SCISSORS, Options.PAPER): (GameResults.WIN, GameResults.LOSE),
        }

        user_choice = Options(user_option)
        enemy_choice = Options(enemy_option)

        if user_choice == enemy_choice:
            game_user.result, game_enemy.result = GameResults.TIE, GameResults.TIE
        else:
            game_user.result, game_enemy.result = results_dict.get((user_choice, enemy_choice), (GameResults.LOSE, GameResults.WIN))

    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    @controller.mark_duplex(Game.IdModel, use_event=True)
    @controller.marshal_ack(Game.IdModel)
    def make_shape_choice(
        self,
        event: DuplexEvent,
        game_id: int,
        room_code: str,
        user: User,
        option: str
    ):
        """Make a shape choice in the game."""
        game = GameRounds.find_by_game_and_user_ids(game_id, user.id)
        game.option = option

        enemy = GameRounds.find_opponent(game_id, user.id)

        if enemy:
            enemys_option = enemy.option
            if enemys_option is not None:
                self.get_results(game_id, user.id, option, enemy.id, enemys_option)
                return event.emit_convert(
                    game,
                    room=room_code,
                )
            return "Opponent's option is not set"

        return "Opponent not found"
