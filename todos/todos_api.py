from datetime import datetime as d

from flask_restx import Resource, fields, abort
from sqlalchemy.exc import IntegrityError

from __lib__.flask_fullstack import ResourceController
from common import sessionmaker
from common.users_db import User
from .todos_db import Todo, TodoCategory
from .parsers import todo_parser, category_parser, by_date_parser

controller = ResourceController("todo", sessionmaker=sessionmaker, path="/")


@controller.route("/todo/")
class TodosList(Resource):
    @controller.response(
        "200 ", 'No any tasks exist', fields.List(fields.Raw(), example=[])
        )
    @controller.jwt_authorizer(User)
    @controller.marshal_list_with(Todo.MainData)
    def get(self, session, user: User):
        return Todo.find_all_by_kwargs(session, creator=user.id)

    @controller.doc_abort(400, "Category does not exist")
    @controller.jwt_authorizer(User)
    @controller.argument_parser(todo_parser)
    @controller.marshal_with(Todo.MainData)
    def post(self, session, name: str, category_id: int,
             date: d, start_time: d, end_time: d, user: User):
        if TodoCategory.find_first_by_kwargs(session, id=category_id):
            task = Todo.create(session, name, category_id, user.id,
                               date.date(), start_time.time(), end_time.time())
            return task
        abort(400, "Category does not exist")


@controller.route("/todo/<int:pk>/")
class TodoCrud(Resource):
    @controller.doc_abort(400, "Task does not exist")
    @controller.jwt_authorizer(User)
    @controller.marshal_with(Todo.MainData)
    def get(self, session, user: User, pk: int):
        return Todo.get_user_task_by_id(session, pk, user.id)

    @controller.response(200, "Success", fields.Raw({'message': 'Updated'}))
    @controller.doc_abort(400, "Task does not exist")
    @controller.jwt_authorizer(User)
    @controller.argument_parser(todo_parser)
    def patch(self, session, name: str, category: int,
              date: d, start_time: d, end_time: d, user: User, pk: int):
        Todo.get_user_task_by_id(
            session, pk, user.id).update(
                name, category, date.date(), start_time.time(), end_time.time()
                )
        return {'message': 'Updated'}

    @controller.response(200, "Success", fields.Raw({'message': 'Deleted'}))
    @controller.doc_abort(400, "Task does not exist.")
    @controller.jwt_authorizer(User)
    def delete(self, session, user: User, pk: int):
        Todo.get_user_task_by_id(session, pk, user.id).delete(session)
        return {'message': 'Deleted'}


@controller.route("/todo/bydate/")
class TodoBydate(Resource):
    @controller.response(
        "200 ", "No any tasks exist", fields.List(fields.Raw(), example=[]))
    @controller.jwt_authorizer(User)
    @controller.argument_parser(by_date_parser)
    @controller.marshal_list_with(Todo.MainData)
    def get(self, session, date: d, user: User):
        return Todo.find_all_by_kwargs(
            session, date=date.date(), creator=user.id
            )


@controller.route("/todo/category/")
class CategoryList(Resource):
    @controller.response(
        "200 ", "No any categories exist", fields.List(
            fields.Raw(), example=[])
            )
    @controller.jwt_authorizer(User)
    @controller.marshal_list_with(TodoCategory.MainData)
    def get(self, session, user: User):
        return TodoCategory.find_all_by_kwargs(session, creator=user.id)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(category_parser)
    @controller.marshal_with(TodoCategory.MainData)
    def post(self, session, name: str, user: User):
        return TodoCategory.create(session, name=name, creator=user.id)


@controller.route("/todo/category/<int:pk>/")
class Category(Resource):
    @controller.doc_abort(400, "Category does not exist")
    @controller.jwt_authorizer(User)
    @controller.marshal_with(TodoCategory.MainData)
    def get(self, session, user: User, pk: int):
        return TodoCategory.get_user_category_by_id(
            session, pk, user.id
            )

    @controller.response(200, "Success", fields.Raw({'message': 'Updated'}))
    @controller.doc_abort(400, "Category does not exist")
    @controller.jwt_authorizer(User)
    @controller.argument_parser(category_parser)
    def patch(self, session, name: str, user: User, pk: int):
        TodoCategory.get_user_category_by_id(session, pk, user.id).update(name)
        return {'message': 'Updated'}

    @controller.response(200, "Success", fields.Raw({'message': 'Deleted'}))
    @controller.doc_abort(400, "Category does not exist")
    @controller.doc_abort(423, "Category is used in a task")
    @controller.jwt_authorizer(User)
    def delete(self, session, user: User, pk: int):
        # Add SQLite3 Foreign Key constraints respect for ondelete restricte
        session.execute('pragma foreign_keys=on')
        try:
            TodoCategory.get_user_category_by_id(
                session, pk, user.id).delete(session)
        except IntegrityError:
            abort(423, "Category is used in a task")
        return {'message': 'Deleted'}
