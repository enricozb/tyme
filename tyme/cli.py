import argparse
import sys

from tyme.timeline import Timeline, TimelineError
from tyme import init as tyme_init


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user",
                        "-u",
                        required=False,
                        default=None,
                        help="Specify a user. If this is not present, then "
                        "the default user is assumed.")

    commands = parser.add_subparsers(title="commands",
                                     required=True,
                                     dest="command",
                                     help="For help on a specific command: "
                                          "`tyme [command] -h`.")

    start = commands.add_parser("start", help="Start a new activity.")
    start.add_argument("activity",
                       metavar="ACTIVITY",
                       help="The activity to be started.")

    stop = commands.add_parser("stop", help="Stop the current activity.")

    make = commands.add_parser("make", help="Make a new activity.")
    make.add_argument("--parents",
                      "-p",
                      action="store_true",
                      help="When creating an activity with an absolute path, "
                      "make any non-existing parents. For example, doing "
                      "`tyme make -p /projects/tyme` "
                      "will create /projects and /projects/tyme if /projects "
                      "doesn't already exist")

    make.add_argument("activity",
                      metavar="ACTIVITY-OR-PATH",
                      help="Create a new activity. The format can either be "
                      "a relative or an absolute path. For example, both "
                      "'cooking' and '/leisure/netflix' are valid examples "
                      "of relative and absolute activities respectively. A "
                      "relative activity will cause an interactive menu to "
                      "appear, in order to decide where to place this "
                      "activity.")

    commands.add_parser("status", help="Output the current activity if any.")

    return parser.parse_args()


def main():
    tyme_init()

    args = parse_args()

    try:
        timeline = Timeline(user=args.user)

        if args.command == "start":
            timeline.start(args.activity, quiet=False)

        elif args.command == "stop" and timeline.current_activity() is not None:
            timeline.done(quiet=False)

        elif args.command == "make":
            timeline.new_activity(args.activity, parents=args.parents)

        elif args.command == "status":
            timeline.print_status()

        timeline.save()

    except TimelineError as e:
        print(e)
