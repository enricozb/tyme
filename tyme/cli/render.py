"""
Render has all of the convenience print functions used by tyme/cli/cli.py
These functions format and color any output that is sent to stdout.
Any fancy output that you see from tyme has been generated here.
"""

import tyme.utils as utils
from tyme.timeline import JSONActivities
from tyme.cli import fzf

from colorama import Fore, Style
from typing import Dict, List, Optional, Tuple
# from pyfzf import FzfPrompt

def start(activity: str,
          done_activity: Tuple[utils.Timestamp, utils.Timestamp, str]) -> None:
    """
    Prints the start activity message, and a done activity message if there
    was an ongoing activity.

    Args:
        activity (str):
            The name of the activity to be started
        done_activity (Tuple[utils.Timestamp, utils.Timestamp, str]):
            The start/end times and name of the just completed activity
    """

    if done_activity is not None:
        done(*done_activity)

    print(f"You started to spend time on ", end="")
    print(f"'{Fore.GREEN + activity + Style.RESET_ALL}'.")


def done(start: utils.Timestamp, end: utils.Timestamp, activity: str) -> None:
    """
    Prints the done activity message.

    Args:
        start (utils.Timestamp): the start time of the activity
        end (utils.Timestamp): the end time of the activity
        activity (str): The name of the activity that was completed
    """

    phrase = format_elapsed_time_phrase(start, end, activity)
    print(f"You spent ", end="")
    print(Fore.YELLOW + Style.BRIGHT + f"({phrase})", end="")
    print(f" on '{Fore.GREEN + activity + Style.RESET_ALL}'.")


def save(timeline_file: str) -> None:
    """
    Prints the timeline saved message.

    Args:
        timeline_file (str): The filename of where the timeline was saved
    """
    print(f"Saved timeline to {timeline_file}")


def format_elapsed_time_phrase(
        start: utils.Timestamp,
        end: utils.Timestamp,
        activity: str) -> str:
    """
    Constructs the human-readable time spent message, such as
    "1 hour and 3 seconds".

    Args:
        start (utils.Timestamp): the start time of the activity
        end (utils.Timestamp): the end time of the activity
        activity (str): The name of the activity

    Returns:
        str: The elapsed time phrase
    """

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
    """
    Prints the status of a potentially ongoing activity.

    Args:
        current_activity (Optional[Dict[str, str]]):
            A dictionary with information about the current activity. The
            expected fields are `"start"`, `"end"`, `"name"` with types
            `util.Timestamp` for the start/end, and `str` for the name.
            If this is `None`, a "no ongoing activity" message is printed.
    """

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
    """
    Prints a log of the given `recent_activities`. Some sections in the log
    that only show elapsed time represent time that was untracked.

    Args:
        recent_activities (Dict[str, List[Dict[str, str]]]):
            A dictionary with information about some recent activities. The
            expected structure is
                {
                    date: [
                        {"start": start_time,
                         "end": end_time,
                         "name": activity_name}
                    ]
                }
    """
    # Show the oldest event first, so the most recent is at the bottom.
    last_end: Optional[utils.Timestamp] = None
    for day in sorted(recent_activities):
        print(Fore.MAGENTA + f"{day}:")
        for activity in recent_activities[day]:
            name = activity["name"]
            start = utils.parse(activity["start"])

            end: Optional[utils.Timestamp] = None
            if "end" in activity:
                end = utils.parse(activity["end"])

            if end is not None:
                phrase = format_elapsed_time_phrase(start,
                                                    end,
                                                    name)
            else:
                phrase = format_elapsed_time_phrase(start,
                                                    utils.utc_now(),
                                                    name)

            # time passed between the end of the last event and the start
            # of this one. Therefore, there is time unaccounted for.
            if last_end is not None and last_end != start:
                untracked_phrase = format_elapsed_time_phrase(last_end,
                                                              start,
                                                              "")

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
    """
    Given a potentially non-absolute activity `activity`, find, the path it
    belongs to. If the activity is not absolute, then a series of interactive
    selections are made in order to determine the destination of the activity.

    Args:
        activity (str): the potentially absolute activity.
        activities (JSONActivities):
            the hierarchy of activities to be used when navigating the tree
            interactively
    """
    # absolute activity path
    if activity.startswith("/"):
        return activity

    elif "/" in activity:
        raise ValueError("names of activities cannot contain '/'")

    # find out the path interactively using fzf
    print("where do you want to place the activity '{activity}'?")
    def enumerate_activity_hierarchy_paths(tree):
      out = []
      for name, (id, subtree) in tree.items():
        out.append(f"{name}/")

      for name, (id, subtree) in tree.items():
        for subpath in enumerate_activity_hierarchy_paths(subtree):
          out.append(f"{name}/{subpath}")
      return out

    path = fzf.iterfzf(["/", *enumerate_activity_hierarchy_paths(activities)])
    if path is None:
        raise RuntimeError("no path was selected")

    return path + activity


def new_activity(activity: str) -> None:
    """
    Prints the new activity message.

    Args:
        activity (str): the activity that was created
    """
    print(f"New activity created at '{activity}'.")
