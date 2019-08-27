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


def format_elapsed_time_phrase(
        start: Timestamp,
        end: Timestamp,
        activity: str,
        ongoing=False,
        short=False) -> str:
    delta = end.datetime - start.datetime

    day = delta.days
    hour = delta.seconds // 3600
    minute = (delta.seconds // 60) % 60
    second = delta.seconds % 60

    phrase = [
        f"{day} {'days' if day > 1 else 'day'}" if day > 0 else "",
        f"{hour} {'hours' if hour > 1 else 'hour'}" if hour > 0 else "",
        f"{minute} {'minutes' if minute > 1 else 'minute'}" if minute > 0 else "",
        f"{second} {'seconds' if second > 1 else 'second'}" if second > 0 else ""
    ]

    # filter out empty strings
    phrase = [p for p in phrase if p != ""]

    # add an 'and' if there is more than one kind of time
    if len(phrase) > 1:
        *rest, last = phrase
        phrase = [*rest, "and", last]

    phrase_str = " ".join(phrase)

    if short:
        return phrase_str

    if ongoing:
        return (f"You are currently spending time on '{activity}'.\n"
                "You have been doing so for " + phrase_str + ".")
    else:
        return "You spent " + phrase_str + f" on '{activity}'."


def print_elapsed_time_phrase(
        start: Timestamp,
        end: Timestamp,
        activity: str,
        ongoing=False,
        short=False) -> None:

    print(format_elapsed_time_phrase(start, end, activity, ongoing, short))


def offset_day(ts: Timestamp, days_offset: int) -> str:
    return (ts.datetime + timedelta(days=days_offset)).date().isoformat()
