from datetime import datetime


def parse_time(date: str) -> datetime:
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")