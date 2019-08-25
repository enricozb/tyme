import argparse
import sys

from tyme.timeline import Timeline, TimelineError
from tyme import init as tyme_init


def parse_args():
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--start",
                        "-s",
                        metavar="ACTIVITY",
                        help="Start a new activity")
    action.add_argument("--done",
                        "-d",
                        action="store_true",
                        help="Finish the current activity")
    action.add_argument("--create-activity",
                        "-c",
                        dest="new_activity",
                        metavar="ACTIVITY-OR-PATH",
                        help="Create a new activity. The format can either be "
                             "a relative or an absolute path.")
    action.add_argument("--create-parents-activity",
                        "-p",
                        dest="new_activity",
                        metavar="ACTIVITY-PATH",
                        help="Create a new activity and parents if they do "
                             "not exist. This is similar to mkdir -p. Careful "
                             "with any typos, as they will be created. If a "
                             "non-absolute path is passed in, this will have "
                             "the same effect as tyme -c.")

    parser.add_argument("--user",
                        "-u",
                        required=False,
                        default=None,
                        help="Specify a user. If this is not present, then "
                             "the default user is assumed.")
    return parser.parse_args()


def main():
    tyme_init()

    args = parse_args()

    try:
        timeline = Timeline(user=args.user)

        if args.start:
            timeline.start(args.start, quiet=False)

        elif args.done and timeline.current_activity() is not None:
            timeline.done(quiet=False)

        elif args.new_activity:
            timeline.new_activity(args.new_activity, parents=True)

        else:
            timeline.print_status()

        timeline.save()

    except TimelineError as e:
        print(e)
