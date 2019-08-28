"""
Convenience functions for converting between datetime and strings when needed
"""

from datetime import datetime, timedelta


day_and_time_format = "%Y-%m-%d_%H:%M:%S"


class Timestamp:
    """
    Convenience strings for formatting a datetime object.

    Args:
        datetime (datetime): the datetime object to be formatted

    Attributes:
        datetime (datetime): the datetime object to be formatted
        date_str (str): the date: YYYY-MM-DD
        time_str (str): the time: HH:MM:SS
        datetime_str (str): the date and time: YYYY-MM-DD_HH:MM:SS

    """

    def __init__(self, datetime: datetime) -> None:
        self.datetime = datetime
        self.date_str: str = datetime.date().isoformat()
        self.time_str: str = datetime.time().isoformat()
        self.datetime_str: str = datetime.strftime(day_and_time_format)

    def __eq__(self, other):
        return self.datetime == other.datetime


def utc_now() -> Timestamp:
    """
    Returns a timestamp of the current UTC time

    Returns:
        Timestamp: the current UTC time
    """
    # to round off milliseconds
    now_str = datetime.utcnow().strftime(day_and_time_format)
    return Timestamp(datetime=datetime.strptime(now_str, day_and_time_format))


def parse(day_and_time: str) -> Timestamp:
    """
    Parses a day_and_time_format string into a Timestamp

    Args:
        day_and_time (str): the day_and_time string to be parsed

    Returns:
        Timestamp: the timestamp with day_and_time as its datetime
    """
    return Timestamp(
        datetime=datetime.strptime(day_and_time, day_and_time_format))


def offset_day(ts: Timestamp, days_offset: int) -> str:
    """
    Returns a the the day given by the Timestamp `ts` offset by `days_offset`.

    Args:
        ts (Timestamp): the time to be offset
        days_offset (int): the number of days to offset by

    Returns:
        str: the date after offsetting `ts` by `days_offset` number of days.
    """
    return (ts.datetime + timedelta(days=days_offset)).date().isoformat()
