from common import (db, db_url, TEST_USERNAME, TEST_PASSWORD, TEST2_USERNAME, TEST2_PASSWORD, SIGN1_NAME, SIGN1_IS_WIN,
                    SIGN2_NAME, SIGN2_IS_WIN, SIGN3_NAME, SIGN3_IS_WIN)
from main import app, socketio


def init_users():
    from common.users_db import User

    if User.find_by_username(TEST_USERNAME) is None:
        User.create(TEST_USERNAME, TEST_PASSWORD)

    if User.find_by_username(TEST_USERNAME) is None:
        User.create(TEST2_USERNAME, TEST2_PASSWORD)


def init_signs_game():
    from common.game_db import Sign

    if Sign.find_by_name(SIGN1_NAME) is None:
        Sign.create(SIGN1_NAME, SIGN1_IS_WIN)

    if Sign.find_by_name(SIGN2_NAME) is None:
        Sign.create(SIGN2_NAME, SIGN2_IS_WIN)

    if Sign.find_by_name(SIGN3_NAME) is None:
        Sign.create(SIGN3_NAME, SIGN3_IS_WIN)


with app.app_context():
    if db_url == "sqlite:///../app.db":
        db.drop_all()
        db.create_all()

    if db_url == "sqlite:///../test.db":
        db.create_all()

    init_users()
    init_signs_game()
    db.session.commit()

app.after_request(db.with_autocommit)
socketio.after_event(db.with_autocommit)

if __name__ == "__main__":  # test only
    socketio.run(app=app, debug=True)
