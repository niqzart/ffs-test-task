from functools import wraps

from flask_socketio import join_room
from pydantic import BaseModel

from __lib__.flask_fullstack import DuplexEvent, EventController
from __lib__.flask_siox import EventSpace
from common import Message, User, sessionmaker

controller = EventController(sessionmaker=sessionmaker)


def check_user_message_owner_or_permitted():
    def check_user_message_owner_or_permitted_wrapper(function):
        @wraps(function)
        @controller.doc_abort(403, "Permission Denied")
        @controller.database_searcher(Message, use_session=True)
        def check_user_message_owner_or_permitted_inner(*args, **kwargs):
            # TODO: add check user permissions level

            user: User = kwargs['user']
            if user.id != kwargs['message'].user_id:
                controller.abort(403, "Permission Denied: It's not your message bruh")

            return function(*args, **kwargs)

        return check_user_message_owner_or_permitted_inner

    return check_user_message_owner_or_permitted_wrapper


@controller.route()
class ChatMessagesEventSpace(EventSpace):
    # TODO: add multi-delete messages

    class MessageTextModel(BaseModel):
        text: str

    class MessageIdModel(BaseModel):
        message_id: int

    class MessageUpdateModel(MessageIdModel, MessageTextModel):
        pass

    @controller.doc_abort(400, "Invalid role")
    @controller.argument_parser(MessageTextModel)
    @controller.mark_duplex(Message.MainData, use_event=True)
    @controller.jwt_authorizer(User)
    @controller.marshal_ack(Message.MainData)
    def new_message(self, event: DuplexEvent, session, user: User, text: str):
        message = Message.create(session, text, user.id)

        event.emit_convert(message, 'global')
        return message

    @controller.argument_parser(MessageIdModel)
    @controller.mark_duplex(MessageIdModel, use_event=True)
    @controller.jwt_authorizer(User)
    @check_user_message_owner_or_permitted()
    @controller.marshal_ack(Message.MainData)
    def delete_message(self, event: DuplexEvent, session, message: Message, **_):
        message = Message.delete(session, message.id)

        event.emit_convert(
            self.MessageIdModel(message_id=message.id),
            'global',
            include_self=True
        )
        return message

    @controller.argument_parser(MessageUpdateModel)
    @controller.mark_duplex(MessageUpdateModel, use_event=True)
    @controller.jwt_authorizer(User)
    @check_user_message_owner_or_permitted()
    @controller.marshal_ack(Message.MainData)
    def update_message(
        self,
        event: DuplexEvent,
        session,
        text: str,
        message: Message,
        **_
    ):
        message = Message.update(session, message.id, text)

        event.emit_convert(
            self.MessageUpdateModel(message_id=message.id, text=message.text),
            'global',
            include_self=True
        )
        return message

    @controller.argument_parser(BaseModel)
    @controller.jwt_authorizer(User)
    @controller.force_ack()
    def start_chat(self, **_):
        join_room("global")
