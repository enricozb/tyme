import os

import hjson

from tyme.common import *
from tyme.timeline import *


__version__ = "0.1.5"


def init():
    """
    Initializes tyme environment with .tyme folder and initial files.
    """

    if not os.path.isdir(TYME_DIR):
        os.mkdir(TYME_DIR)
        os.mkdir(TYME_TIMELINES_DIR)

    if not os.path.exists(TYME_STATE_FILE):
        print("Couldn't find any users, tyme has probably not been setup yet.")
        user = input("What user would you like to use for your timeline?\n"
                     "username: ")
        state = {'default_user': user}

        with open(TYME_STATE_FILE, 'w') as state_file:
            hjson.dump(state, state_file)

        Timeline.make_empty(user)
