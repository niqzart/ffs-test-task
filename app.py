from common.constants import TEST_USERNAME, TEST_PASSWORD
from common.config import db, db_url
from common import (
    TEST_USERNAME2,
    TEST_PASSWORD2,
    TEST_GAME_ID,
    TEST_USER1_ID,
    TEST_USER2_ID,
    TEST_USER1_OPTION,
    TEST_USER2_OPTION,
    TEST_USER1_RESULT,
    TEST_USER2_RESULT
)

from main import app, socketio

def init_users():
    """
    Initialize users if they do not exist.
    """
    from common.users_db import User

    if User.find_by_username(TEST_USERNAME) is None:
        User.create(TEST_USERNAME, TEST_PASSWORD)

    if User.find_by_username(TEST_USERNAME2) is None:
        User.create(TEST_USERNAME2, TEST_PASSWORD2)

def init_game():
    """
    Initialize the game if it does not exist.
    """
    from game.game_db import Game, GameRounds

    if Game.find_by_id(TEST_GAME_ID) is None:
        Game.create(game_id=TEST_GAME_ID)

    GameRounds.create(game_id=TEST_GAME_ID, user_id=TEST_USER1_ID, option=TEST_USER1_OPTION, result=TEST_USER1_RESULT)
    GameRounds.create(game_id=TEST_GAME_ID, user_id=TEST_USER2_ID, option=TEST_USER2_OPTION, result=TEST_USER2_RESULT)

with app.app_context():
    if db_url == "sqlite:///../app.db":
        db.drop_all()
        db.create_all()

    if db_url == "sqlite:///../test.db":
        db.create_all()

    init_users()
    init_game()
    db.session.commit()

app.after_request(db.with_autocommit)
socketio.after_event(db.with_autocommit)

if __name__ == "__main__":  
    socketio.run(app=app, debug=True)
