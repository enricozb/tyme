import uuid
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import hjson
from colorama import Fore, Style

import tyme.utils as utils
from tyme.common import *


JSONTimeline = Dict[str, List[Dict[str, str]]]
JSONActivities = Dict[str, Tuple[str, "JSONActivities"]]


class TimelineError(Exception):
    pass


class Timeline:
    """
    Interface to modify timeline data. Create new activity categories, start
    or finish activities, and query statistics about them.
    """

    def __init__(self,
                 user: str = None,
                 timeline: JSONTimeline = None,
                 activities: JSONActivities = None) -> None:
        """
        Creates a timeline with a user. If a user is not specified, then
        the defauly user is used. If a user is specified, then that user's
        timeline is loaded, unless timeline & activities are also passed in.
        """
        if user is None:
            user = Timeline.default_user()
        self.user = user

        if timeline is not None and activities is not None:
            self.timeline = timeline
            self.activities = activities

        elif timeline is None and activities is None:
            user_state = Timeline.load_user_timeline(user)
            self.timeline = user_state["timeline"]
            self.activities = user_state["activities"]

        else:
            raise ValueError(
                "both timeline and activies must have values or be None")

    def print_status(self) -> None:
        current_activity = self.current_activity()
        if current_activity is None:
            print("There is no ongoing activity.")

        else:
            start_timestamp = utils.parse(current_activity["start"])
            end_timestamp = utils.utc_now()

            utils.print_elapsed_time_phrase(start_timestamp,
                                            end_timestamp,
                                            current_activity["name"],
                                            ongoing=True)

    def print_log(self, num: int = 5) -> None:
        def most_recent_activities(num) -> Dict[str, List[Dict[str, str]]]:
            count = 0

            # `activities`: a map from day (str) to a list of timeline entries
            activities: Dict[str, List[Dict[str, str]]] = defaultdict(list)

            # Grab the most recent `num` events
            for day in sorted(self.timeline.keys(), reverse=True):
                for activity in self.timeline[day][::-1]:
                    # not a real activity, but a link to one on a previous day
                    if "previous" in activity:
                        continue

                    activities[day].append(activity)

                    count += 1
                    if count == num:
                        return dict(activities)

            return dict(activities)

        activities = most_recent_activities(num)

        # Show the oldest event first, so the most recent is at the bottom.
        last_end: Optional[utils.Timestamp] = None
        for day in sorted(activities):
            print(f"On {day}:")
            for activity in activities[day][::-1]:
                name = activity["name"]
                start = utils.parse(activity["start"])

                end: Optional[utils.Timestamp] = None
                if "end" in activity:
                    end = utils.parse(activity["end"])

                if end is not None:
                    phrase = utils.format_elapsed_time_phrase(start,
                                                              end,
                                                              name,
                                                              short=True)
                else:
                    phrase = utils.format_elapsed_time_phrase(start,
                                                              utils.utc_now(),
                                                              name,
                                                              short=True)

                # time passed between the end of the last event and the start
                # of this one. Therefore, there is time unaccounted for.
                if last_end is not None and last_end != start:
                    unalloc_phrase = utils.format_elapsed_time_phrase(
                        last_end, start, "", short=True)

                    print(Fore.RED + " |")
                    print(Style.DIM + Fore.RED + " |", end="")
                    print(Fore.RED + f" ({unalloc_phrase})")
                    print(Fore.RED + " |")

                else:
                    print(Fore.BLUE + " V")

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

    def start(self, activity: str, quiet: bool=True) -> None:
        """
        Completes any ongoing activity and starts a new one.
        """
        activity_id = self.activity_id(activity)
        if activity_id is None:
            raise TimelineError(f"The activity '{activity}' does not exist.")

        if self.current_activity() is not None:
            self.done(quiet=quiet)

        start_timestamp = utils.utc_now()
        if start_timestamp.date_str not in self.timeline:
            self.timeline[start_timestamp.date_str] = []

        self.timeline[start_timestamp.date_str].append({
            "id": activity_id,
            "name": activity,
            "start": start_timestamp.datetime_str
        })

        if not quiet:
            print(f"You started to spend time on '{activity}'.")

    def done(self, quiet: bool=True) -> None:
        # grab the most recent day and the most recent activity on that day
        last_activity = self.timeline[sorted(self.timeline.keys())[-1]][-1]

        start_timestamp = utils.parse(last_activity["start"])
        end_timestamp = utils.utc_now()

        last_activity["end"] = end_timestamp.datetime_str
        if not quiet:
            utils.print_elapsed_time_phrase(start_timestamp,
                                            end_timestamp,
                                            last_activity["name"])

        # if the ongoing activity was started today, we're done.
        if start_timestamp.date_str == end_timestamp.date_str:
            return

        # otherwise, fill any days in between the start time and today
        # quickly check that start time is not in the future.
        if start_timestamp.date_str > end_timestamp.date_str:
            raise TimelineError("Finishing activity before it was started. "
                                "Maybe system clock is wrong?")

        num_days = end_timestamp.datetime.day - start_timestamp.datetime.day
        for offset in range(1, num_days + 1):
            day = utils.offset_day(start_timestamp, days_offset=offset)
            self.timeline[day] = [
                {
                    "id": last_activity["id"],
                    "name": last_activity["name"],
                    "start": last_activity["start"],
                    "end": end_timestamp.datetime_str,
                    "previous": "",
                }
            ]

    def current_activity(self) -> Optional[Dict[str, str]]:
        if self.timeline == {}:
            return None

        last_activity = self.timeline[sorted(self.timeline.keys())[-1]][-1]

        if "end" in last_activity:
            return None

        return last_activity

    def save(self, quiet=True):
        timeline_file = (TYME_TIMELINES_DIR / self.user).with_suffix(".hjson")
        if not quiet:
            print(f"Saving timeline to {timeline_file}")

        with open(timeline_file, "w") as timeline:
            hjson.dump({"timeline": self.timeline,
                        "activities": self.activities},
                       timeline)

    def new_activity(self, activity, parents=False):
        """
        Creates a new activity. `activity` can either be a single name or a
        path of the form /path/to/activity. If the activity is not a path,
        then a cli interface will come up allowing the user to select where
        in the hierarchy this activity should be created. If a path of the
        form /p1/p2/p3/.../pn is passed in, then p1 through p(n-1) must exist
        in that order and pn will be the new activity.

        If parents is true, the parents of an absolute activity path /p1/.../pn
        will also be created if they do not exist.
        """
        if activity.startswith("/"):
            activity_path = activity.split("/")[1:]
            if "" in activity_path:
                raise ValueError("malformed absolute activity path")

            *path, new_activity = activity_path

            current_category = self.activities
            for category in path:
                if category not in current_category:
                    if not parents:
                        raise ValueError(f"the activity '{category}' within "
                                         f"'{activity}' does not exist")
                    else:
                        # just make a new activity.
                        current_category[category] = (str(uuid.uuid4()), {})

                # [1] is because the first element in each activity is a uuid
                current_category = current_category[category][1]

            current_category[new_activity] = (str(uuid.uuid4()), {})

        elif "/" in activity:
            raise ValueError("names of activities cannot contain '/'")

        else:
            current_category = self.activities
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
                cat = input("Under which category should this activity be "
                            f"placed? [0-{num_categories}] ")
                print()
                if not (cat.isnumeric() and 0 <= int(cat) <= num_categories):
                    print("invalid category choice!")
                    continue

                cat = int(cat)

                if cat == 0:
                    break
                else:
                    path += categories[cat - 1] + "/"
                    current_category = current_category[categories[cat - 1]][1]

            current_category[activity] = (str(uuid.uuid4()), {})
            print(f"activity created at '{path + activity}'")

    def activity_id(self, activity: str) -> Optional[str]:
        def search(category: JSONActivities) -> Optional[str]:
            children = category
            for cat_name, (cat_id, cat_children) in children.items():
                if cat_name == activity:
                    return cat_id

                potential_id = search(cat_children)
                if potential_id is not None:
                    return potential_id

            return None

        return search(self.activities)

    @staticmethod
    def make_empty(user: str):
        Timeline(user=user, timeline={}, activities={}).save(quiet=False)

    @staticmethod
    def default_user() -> str:
        with open(TYME_STATE_FILE) as state_file:
            return hjson.load(state_file)["default_user"]

    @staticmethod
    def load_user_timeline(user: str):
        user_timeline_path = (TYME_TIMELINES_DIR / user).with_suffix(".hjson")
        with open(user_timeline_path) as timeline:
            return hjson.load(timeline)
