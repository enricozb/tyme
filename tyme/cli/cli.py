"""
Entrypoint for tyme cli
"""

import argparse
import sys

import colorama

import tyme.cli.render as render
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

    parser.add_argument("--no-color",
                        "-c",
                        required=False,
                        action="store_true",
                        help="Disable colors globally.")

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

    log = commands.add_parser("log",
                              help="Get a log of some recent activities. "
                                   "Tracked sections of time are blue. "
                                   "Untracked sections of time are red.")
    log.add_argument("number",
                     nargs="?",
                     default=5,
                     type=int,
                     help="The number of events to display. Defaults to 5.")

    where = commands.add_parser("where",
                                help="Get the full path of an activity.")

    where.add_argument("activity",
                       metavar="Activity",
                       help="The activity whose path is to be determined.")
    return parser.parse_args()


def main():
    """
    Entrypoint for tyme's cli.
    """

    tyme_init()
    args = parse_args()

    if args.no_color:
        colorama.init(autoreset=True, strip=True, convert=False)
    else:
        colorama.init(autoreset=True)

    try:
        timeline = Timeline(user=args.user)

        if args.command == "start":
            done_activity = timeline.start(args.activity)
            render.start(args.activity, done_activity)

        elif args.command == "stop" and timeline.current_activity() is not None:
            start, end, activity = timeline.done()
            render.done(start, end, activity)

        elif args.command == "make":
            activity = render.select_activity_path(args.activity,
                                                   timeline.activities)
            timeline.new_activity(activity, parents=args.parents)
            render.new_activity(activity)

        elif args.command == "status":
            render.print_status(timeline.current_activity())

        elif args.command == "log":
            recent_activities = timeline.recent_activities(num=args.number)
            render.print_log(recent_activities)

        elif args.command == "where":
            print(timeline.activity_path(args.activity))

        timeline.save()

    except TimelineError as e:
        print(e)
