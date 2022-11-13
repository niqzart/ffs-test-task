from flask_fullstack import DuplexEvent, EventSpace, EventController
from common import User, CategoryTodo, db
from todo.config import UserRoom

controller: EventController = EventController()


@controller.route()
class CategoryEventSpace(EventSpace, UserRoom):
    class CreateModel(CategoryTodo.CreationBaseModel, UserRoom.UserIdModel):
        pass

    @controller.argument_parser(CreateModel)
    @controller.mark_duplex(CategoryTodo.IndexModel, use_event=True)
    @controller.jwt_authorizer(User)
    @controller.marshal_ack(CategoryTodo.BaseModel)
    def new_category(
            self,
            event: DuplexEvent,
            name: str,
            user: User
    ):
        category = CategoryTodo.create(name=name, user_id=user.id)
        event.emit_convert(category, self.room_name(user.id))

    class UpdateModel(CategoryTodo.CreationBaseModel, UserRoom.UserIdModel):
        category_id: int

    @controller.argument_parser(UpdateModel)
    @controller.mark_duplex(CategoryTodo.IndexModel, use_event=True)
    @controller.jwt_authorizer(User)
    @controller.database_searcher(CategoryTodo)
    @controller.marshal_ack(CategoryTodo.IndexModel)
    def update_category(
            self,
            event: DuplexEvent,
            name: str,
            user: User,
            category: CategoryTodo
    ):
        if name is not None:
            category.name = name
        db.session.commit()

        event.emit_convert(category, self.room_name(user.id))
        return category

    class DeleteModel(UserRoom.UserIdModel):
        category_id: int

    @controller.argument_parser(DeleteModel)
    @controller.mark_duplex(DeleteModel, use_event=True)
    @controller.jwt_authorizer(User)
    @controller.database_searcher(CategoryTodo)
    @controller.force_ack()
    def delete_category(
            self,
            event: DuplexEvent,
            user: User,
            category: CategoryTodo
    ):
        category.delete()
        db.session.commit()
        event.emit_convert(
            room=self.room_name(user.id),
            user_id=user.id,
            category_id=category.id
        )
