from datetime import datetime, timedelta


day_and_time_format = "%Y-%m-%d_%H:%M:%S"


class Timestamp:
    def __init__(self, datetime: datetime) -> None:
        self.datetime = datetime
        self.date_str: str = datetime.date().isoformat()
        self.time_str: str = datetime.time().isoformat()
        self.datetime_str: str = datetime.strftime(day_and_time_format)

    def __eq__(self, other):
        return self.datetime == other.datetime


def utc_now() -> Timestamp:
    # to round off milliseconds
    now_str = datetime.utcnow().strftime(day_and_time_format)
    return Timestamp(datetime=datetime.strptime(now_str, day_and_time_format))


def parse(day_and_time: str) -> Timestamp:
    return Timestamp(
        datetime=datetime.strptime(day_and_time, day_and_time_format))


def offset_day(ts: Timestamp, days_offset: int) -> str:
    return (ts.datetime + timedelta(days=days_offset)).date().isoformat()
