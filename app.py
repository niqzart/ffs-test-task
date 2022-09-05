from common import sessionmaker, db_url, db_meta, TEST_USERNAME, TEST_PASSWORD
from main import app, socketio

if db_url == "sqlite:///app.db":
    # db_meta.drop_all()
    db_meta.create_all()

if db_url == "sqlite:///test.db":
    db_meta.create_all()


@sessionmaker.with_begin
def init_users(session):
    from common.users_db import User

    if User.find_by_username(session, TEST_USERNAME) is None:
        User.create(session, TEST_USERNAME, TEST_PASSWORD)


# init_users()

if __name__ == "__main__":  # test only
    socketio.run(app=app, debug=True)
