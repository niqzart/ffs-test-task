from flask_restx import inputs
from flask_restx.reqparse import RequestParser

from .utils import get_time

todo_parser: RequestParser = RequestParser()
todo_parser.add_argument(
    "name", type=str, required=True, help="A task description"
    )
todo_parser.add_argument(
    "category_id", type=int, required=True, help="ID of existing category"
    )
todo_parser.add_argument(
    "date", type=inputs.date, required=True, help="Date format YYYY-MM-DD"
    )
todo_parser.add_argument(
    "start_time", type=get_time, required=True, help="Time format HH:MM"
    )
todo_parser.add_argument(
    "end_time", type=get_time, required=True, help="Time format HH:MM"
    )

by_date_parser: RequestParser = RequestParser()
by_date_parser.add_argument(
    "date", type=inputs.date, required=True, help="Date format YYYY-MM-DD"
    )

category_parser: RequestParser = RequestParser()
category_parser.add_argument(
    "name", type=str, required=True, help="A category name"
    )
