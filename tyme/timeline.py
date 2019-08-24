import uuid
from typing import Dict, List, Tuple

import hjson

from tyme.common import *


JSONTimeline = Dict[str, List[Dict[str, str]]]
JSONActivities = Dict[str, Tuple[str, 'JSONActivities']]


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

    def save(self, quiet=True):
        timeline_file = (TYME_TIMELINES_DIR / self.user).with_suffix('.hjson')
        if not quiet:
            print(f"Saving timeline to {timeline_file}")

        with open(timeline_file, 'w') as timeline:
            hjson.dump({'timeline': self.timeline,
                        'activities': self.activities},
                       timeline)

    def new_activity(self, activity):
        """
        Creates a new activity. `activity` can either be a single name or a
        path of the form /path/to/activity. If the activity is not a path,
        then a cli interface will come up allowing the user to select where
        in the hierarchy this activity should be created. If a path of the
        form /p1/p2/p3/.../pn is passed in, then p1 through p(n-1) must exist
        in that order and pn will be the new activity.
        """
        if activity.startswith("/"):
            activity_path = activity.split("/")[1:]
            if '' in activity_path:
                raise ValueError("malformed absolute activity path")

            *path, new_activity = activity_path

            current_category = self.activities
            for category in path:
                if category not in current_category:
                    raise ValueError(f"the activity '{category}' within "
                                     "'{activity}' does not exist")

                # [1] is because the first element in each activity is a uuid
                current_category = current_category[category][1]

            current_category[new_activity] = (str(uuid.uuid4()), {})

        elif "/" in activity:
            raise ValueError("names of activities cannot contian '/'")

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
            print(f"activity {activity} created under {path}")

    @staticmethod
    def make_empty(user: str):
        Timeline(user=user, timeline={}, activities={}).save(quiet=False)

    @staticmethod
    def default_user() -> str:
        with open(TYME_STATE_FILE) as state_file:
            return hjson.load(state_file)['default_user']

    @staticmethod
    def load_user_timeline(user: str):
        user_timeline_path = (TYME_TIMELINES_DIR / user).with_suffix(".hjson")
        with open(user_timeline_path) as timeline:
            return hjson.load(timeline)
