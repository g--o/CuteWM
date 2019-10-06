'''
CuteWM
===================== credits =====================
based on
simplewm.py
By Joshua D. Bartlett, March 2011
'''

import sys
import traceback
import os

import wm_core
from wm_common import *
from wm_config import *

def main():
    try:
        wm = wm_core.CuteWM()
    except NoUnmanagedScreens:
        Logger.err('No unmanaged screens found')
        return 2

    try:
        # start CuteWM
        os.system(" ".join(SESSION_INIT_COMMAND))
        wm.main_loop()
    # exception handling
    except KeyboardInterrupt:
        print
        return 0
    except SystemExit:
        raise
    except:
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
