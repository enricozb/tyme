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
                "Both timeline and activies must have values or be None")

    def save(self, quiet=True):
        timeline_file = (TYME_TIMELINES_DIR / self.user).with_suffix('.hjson')
        if not quiet:
            print(f"Saving timeline to {timeline_file}")

        with open(timeline_file, 'w') as timeline:
            hjson.dump({'timeline': self.timeline,
                        'activities': self.activities},
                       timeline)

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
