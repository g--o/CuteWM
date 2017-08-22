
from wm_utils import *
from wm_common import *
import wm_events

class CuteWM(object):
    def __init__(self):
        # initialize members
        if Xlib.__version__ < REQUIRED_XLIB_VERSION:
            print >> sys.stderr, 'Xlib version 0.14 is required, {ver} was found'.format(ver='.'.join(str(i) for i in Xlib.__version__))
            raise InsufficientXlibVersion()
        self.display, self.appname, self.resource_database, self.args = Xlib.rdb.get_display_opts(Xlib.rdb.stdopts)
        self.drag_window = None
        self.drag_offset = (0, 0)
        self.screens = []
        self.event_handler = wm_events.EventHandler(self)

        # initialize display
        if self.display is not None:
            os.environ['DISPLAY'] = self.display.get_display_name()

        # init screens to be managed
        for screen_id in xrange(0, self.display.screen_count()):
            if self.event_handler.redirect_screen_events(screen_id):
                self.screens.append(screen_id)
        # check if no screens has been found
        if len(self.screens) == 0:
            raise NoUnmanagedScreens()
        self.display.set_error_handler(self.x_error_handler)

    def handle_window_drag(self, window, root_x, root_y):
        if self.drag_window is None:
            # Start drag
            self.drag_window = window
            geo = self.drag_window.get_geometry()
            self.drag_offset = geo.x - root_x, geo.y - root_y
        else:
            # Continue drag
            x, y = self.drag_offset
            self.drag_window.configure(x=x + root_x, y=y + root_y)

    def x_error_handler(self, err, request):
        print >> sys.stderr, 'X protocol error: {0}'.format(err)

    def handle_event(self):
        '''
        Wait for the next event and handle it.
        '''
        try:
            # fetch event
            event = self.display.next_event()
        except Xlib.error.ConnectionClosedError:
            print >> sys.stderr, 'Display connection closed by server'
            raise KeyboardInterrupt

        self.event_handler.handle(event)

    def main_loop(self):
        '''
        Loop until Ctrl+C or exceptions have occurred more than MAX_EXCEPTION times.
        '''
        errors = 0
        while True:
            try:
                self.handle_event()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                errors += 1
                if errors > MAX_EXCEPTIONS:
                    raise
                    traceback.print_exc()
