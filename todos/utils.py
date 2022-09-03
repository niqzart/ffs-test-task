from datetime import datetime


def get_time(time):
    return datetime.strptime(time, "%H:%M")
