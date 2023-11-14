from common.config import db_url, db
from common.constants import TEST_USERNAME, TEST_PASSWORD
from main import app, socketio


def init_users():
    from common.users_db import User

    if User.find_by_username(TEST_USERNAME) is None:
        User.create(TEST_USERNAME, TEST_PASSWORD)


with app.app_context():
    if db_url == "sqlite:///../app.db":
        db.drop_all()
        db.create_all()

    if db_url == "sqlite:///../test.db":
        db.create_all()

    init_users()
    db.session.commit()

app.after_request(db.with_autocommit)
socketio.after_event(db.with_autocommit)

if __name__ == "__main__":  # test only
    socketio.run(app=app, debug=True)
