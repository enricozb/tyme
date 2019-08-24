import argparse
import sys

from tyme.timeline import Timeline
from tyme import init


def parse_args():
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--start",
                        "-s",
                        metavar="ACTIVITY",
                        help="Start a new activity")
    action.add_argument("--done",
                        "-d",
                        metavar="ACTIVITY",
                        help="Finish the current activity")
    action.add_argument("--create-activity",
                        "-c",
                        dest="new_activity",
                        metavar="ACTIVITY",
                        help="Create a new activity. The format can either be "
                             "a relative or an absolute path.")

    parser.add_argument("--user",
                        "-u",
                        required=False,
                        default=None,
                        help="Specify a user. If this is not present, then "
                             "the default user is assumed.")
    return parser.parse_args()


def main():
    init()

    args = parse_args()

    timeline = Timeline(user=args.user)

    if args.start:
        timeline.start(args.start)

    elif args.done:
        activity, time = timeline.done()
        print(f"You spent {elapsed_time_phrase(time)} on '{activity}'")

    elif args.new_activity:
        timeline.new_activity(args.new_activity)

    timeline.save()
