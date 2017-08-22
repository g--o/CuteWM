import os
import sys
import traceback

import Xlib.rdb, Xlib.X, Xlib.XK

REQUIRED_XLIB_VERSION = (0, 14)
MAX_EXCEPTIONS = 25
XTERM_COMMAND = ['/usr/bin/xterm']
RELEASE_MODIFIER = Xlib.X.AnyModifier << 1

def child_clear():
    '''
    Clears all parent's stuff
    '''
    os.chdir(os.path.expanduser('~'))
    os.umask(0)
    # Close all file descriptors.
    import resource
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = 1024
    for fd in xrange(maxfd):
        try:
            os.close(fd)
        except OSError:
            pass
    # Open /dev/null for stdin, stdout, stderr.
    os.open('/dev/null', os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)

# system() replacing os.system()
def system(command):
    '''
    Forks a command and disowns it.
    '''
    if os.fork() != 0:
        return

    try:
        # Child.
        os.setsid()     # Become session leader.
        if os.fork() != 0:
            os._exit(0)

        child_clear()
        os.execve(command[0], command, os.environ)
    except:
        try:
            # Error in child process.
            print >> sys.stderr, 'Error in child process:'
            traceback.print_exc()
        except:
            pass
        sys.exit(1)

def getMask(btId):
    BASE_POWER = 7
    return pow(2, BASE_POWER + btId)
