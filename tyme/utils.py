from datetime import datetime, timedelta


day_and_time_format = "%Y-%m-%d_%H:%M:%S"


class Timestamp:
    def __init__(self, datetime: datetime) -> None:
        self.datetime = datetime
        self.date_str: str = datetime.date().isoformat()
        self.datetime_str: str = datetime.strftime(day_and_time_format)


def utc_now() -> Timestamp:
    # to round off milliseconds
    now_str = datetime.utcnow().strftime(day_and_time_format)
    return Timestamp(datetime=datetime.strptime(now_str, day_and_time_format))


def parse(day_and_time: str) -> Timestamp:
    return Timestamp(
        datetime=datetime.strptime(day_and_time, day_and_time_format))


def print_elapsed_time_phrase(
        start: Timestamp,
        end: Timestamp,
        activity: str,
        ongoing=False) -> None:
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

    if ongoing:
        print(f"You are currently doing '{activity}'.")
        print("You have been doing so for " + " ".join(phrase) + ".")
    else:
        print("You spent " + " ".join(phrase) + f" on '{activity}'.")


def offset_day(ts: Timestamp, days_offset: int) -> str:
    return (ts.datetime + timedelta(days=days_offset)).isoformat()
