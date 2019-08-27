from typing import Dict, List, Optional, Tuple

from colorama import Fore, Style

import tyme.utils as utils
from tyme.timeline import JSONActivities


def start(activity: str,
          done_activity: Tuple[utils.Timestamp, utils.Timestamp, str]) -> None:

    if done_activity is not None:
        done(*done_activity)

    print(f"You started to spend time on ", end="")
    print(f"'{Fore.GREEN + activity + Style.RESET_ALL}'.")


def done(start: utils.Timestamp, end: utils.Timestamp, activity: str) -> None:
    phrase = format_elapsed_time_phrase(start, end, activity)
    print(f"You spent ", end="")
    print(Fore.YELLOW + Style.BRIGHT + f"({phrase})", end="")
    print(f" on '{Fore.GREEN + activity + Style.RESET_ALL}'.")


def save(timeline_file: str) -> None:
    print(f"Saving timeline to {timeline_file}")


def format_elapsed_time_phrase(
        start: utils.Timestamp,
        end: utils.Timestamp,
        activity: str,
        short=False) -> str:
    delta = end.datetime - start.datetime

    day = delta.days
    hour = delta.seconds // 3600
    minu = (delta.seconds // 60) % 60
    sec = delta.seconds % 60

    phrase = [
        f"{day} {'days' if day > 1 else 'day'}" if day > 0 else "",
        f"{hour} {'hours' if hour > 1 else 'hour'}" if hour > 0 else "",
        f"{minu} {'minutes' if minu > 1 else 'minute'}" if minu > 0 else "",
        f"{sec} {'seconds' if sec > 1 else 'second'}" if sec > 0 else ""
    ]

    # filter out empty strings
    phrase = [p for p in phrase if p != ""]

    # add an 'and' if there is more than one kind of time
    if len(phrase) > 1:
        *rest, last = phrase
        phrase = [*rest, "and", last]

    return " ".join(phrase)


def print_status(current_activity: Optional[Dict[str, str]]) -> None:
    if current_activity is None:
        return print("There is no ongoing activity.")

    start_timestamp = utils.parse(current_activity["start"])
    end_timestamp = utils.utc_now()

    phrase = format_elapsed_time_phrase(start_timestamp,
                                        end_timestamp,
                                        current_activity["name"])

    name = current_activity["name"]

    print(Fore.BLUE + f" |-", end="")
    print(Fore.GREEN + f"{name}", end="")
    print(Style.BRIGHT + Fore.YELLOW + f" ({phrase}):")
    print(Fore.BLUE + f" |", end="")
    print(f"   start: ", end="")
    print(Fore.YELLOW + f"{start_timestamp.time_str}")

    print(Fore.BLUE + " |", end="")
    print(f"   end:   ", end="")
    print(Fore.YELLOW + "...")
    print(Fore.BLUE + " V")


def print_log(recent_activities: Dict[str, List[Dict[str, str]]]) -> None:
    # Show the oldest event first, so the most recent is at the bottom.
    last_end: Optional[utils.Timestamp] = None
    for day in sorted(recent_activities):
        print(Fore.MAGENTA + f"{day}:")
        for activity in recent_activities[day][::-1]:
            name = activity["name"]
            start = utils.parse(activity["start"])

            end: Optional[utils.Timestamp] = None
            if "end" in activity:
                end = utils.parse(activity["end"])

            if end is not None:
                phrase = format_elapsed_time_phrase(start,
                                                    end,
                                                    name,
                                                    short=True)
            else:
                phrase = format_elapsed_time_phrase(start,
                                                    utils.utc_now(),
                                                    name,
                                                    short=True)

            # time passed between the end of the last event and the start
            # of this one. Therefore, there is time unaccounted for.
            if last_end is not None and last_end != start:
                untracked_phrase = format_elapsed_time_phrase(last_end,
                                                              start,
                                                              "",
                                                              short=True)

                print(Fore.RED + " |")
                print(Style.DIM + Fore.RED + " |", end="")
                print(Fore.RED + f" ({untracked_phrase})")
                print(Fore.RED + " |")

            print(Fore.BLUE + f" |-", end="")
            print(Fore.GREEN + f"{name}", end="")
            print(Style.BRIGHT + Fore.YELLOW + f" ({phrase}):")
            print(Fore.BLUE + f" |", end="")
            print(f"   start: ", end="")
            print(Fore.YELLOW + f"{start.time_str}")

            print(Fore.BLUE + " |", end="")
            if end is None:
                print(Fore.YELLOW + "          ...")
            else:
                print(f"   end:   ", end="")
                print(Fore.YELLOW + f"{end.time_str}")

            last_end = end

            print(Fore.BLUE + " V")


def select_activity_path(activity: str, activities: JSONActivities) -> str:
    # absolute activity path
    if activity.startswith("/"):
        return activity

    elif "/" in activity:
        raise ValueError("names of activities cannot contain '/'")

    # otherwise, find out the path interactively
    current_category = activities
    path = "/"
    while True:
        categories = list(current_category.keys())

        if len(categories) == 0:
            break

        print("0) here (at this level in the category hierarchy)")
        for i, category in enumerate(categories):
            print(f"{i + 1}) {category}")

        num_categories = len(current_category.keys())

        print()
        index = input("Under which category should this activity be "
                      f"placed? [0-{num_categories}] ")
        print()
        if not (index.isnumeric() and 0 <= int(index) <= num_categories):
            print("invalid category choice!")
            continue

        cat = int(index)

        if cat == 0:
            break
        else:
            path += categories[cat - 1] + "/"
            current_category = current_category[categories[cat - 1]][1]

    return path + activity


def new_activity(activity: str) -> None:
    print(f"New activity created at '{activity}'.")
