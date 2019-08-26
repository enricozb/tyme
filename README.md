# tyme
A command-line utility (soon to be joined by an iOS app) that lets you track
what you spend your time on.

## Installation
```bash
pip install tyme --user
```
the `--user` flag might not be necessary if you own your machine. Make sure
it installs completely as you want access to the `tyme` script.

## Usage

### First Time Setup
tyme needs to be initialized before any command runs. This can be done by
just running
```
tyme
```

### Creating and Tracking Your First Activity
Then, you can create some simple activity hierarchy,
```
[enricozb : ~] tyme make -p /leisure/cooking
[enricozb : ~] tyme start cooking

You started to spend time on 'cooking'.
```

You can also interactively create an activity like so,
```
[enricozb : ~] tyme make "video games"

0) here (at this level in the category hierarchy)
1) projects
2) social
3) leisure

Under which category should this activity be placed? [0-3] 3

0) here (at this level in the category hierarchy)
1) cooking

Under which category should this activity be placed? [0-1] 0

activity created at '/leisure/video games'
```

### Additional Help
For general help on how the command-line interface works, just type
```
tyme -h
```
and for specific help on one of the tyme commands, type
```
tyme [command] -h
```
for example,
```
[enricozb : ~] tyme make -h

usage: tyme make [-h] [--parents] ACTIVITY-OR-PATH

positional arguments:
  ACTIVITY-OR-PATH  Create a new activity. The format can either be a relative
                    or an absolute path. For example, both 'cooking' and
                    '/leisure/netflix' are valid examples of relative and
                    absolute activities respectively. A relative activity will
                    cause an interactive menu to appear, in order to decide
                    where to place this activity.

optional arguments:
  -h, --help        show this help message and exit
  --parents, -p     When creating an activity with an absolute path, make any
                    non-existing parents. For example, doing `tyme make -p
                    /projects/tyme` will create /projects and /projects/tyme
                    if /projects doesn't already exist
```
