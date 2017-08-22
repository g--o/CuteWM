
import Xlib.rdb, Xlib.X
import key_bindings

from key_defs import *
from wm_utils import *

class EventHandler(object):
    def __init__(self, wm):
        # "jump-table" for events
        self.event_dispatch_table = {
            Xlib.X.MapRequest: self.handle_map_request,
            Xlib.X.ConfigureRequest: self.handle_configure_request,
            Xlib.X.MappingNotify: self.handle_mapping_notify,
            Xlib.X.MotionNotify: self.handle_mouse_motion,
            Xlib.X.ButtonPress: self.handle_mouse_press,
            Xlib.X.ButtonRelease: self.handle_mouse_release,
            Xlib.X.KeyPress: self.handle_key_press,
            Xlib.X.KeyRelease: self.handle_key_release,
        }

        self.wm = wm
        # set enter (return) key code.
        self.enter_codes = set(code for code, index in self.wm.display.keysym_to_keycodes(Xlib.XK.XK_Return))

    def handle(self, event):
            # check if in our event dispatch table
            if event.type in self.event_dispatch_table:
                handler = self.event_dispatch_table[event.type]
                handler(event)
            else:
                # we can't handle the event. log it.
                print 'unhandled event: {event}'.format(event=event)

    def get_event_dispatch_table(self):
        return self.event_dispatch_table

    def get_enter_codes(self):
        return self.enter_codes

    def grab_window_events(self, window):
        '''
        Grab drag events on the window.
        '''
        window.grab_button(key_bindings.GRAB_BUTTON,
            key_bindings.MOD_KEY & ~RELEASE_MODIFIER, True,
            Xlib.X.ButtonMotionMask | Xlib.X.ButtonReleaseMask,
            Xlib.X.GrabModeAsync,
            Xlib.X.GrabModeAsync,
            Xlib.X.NONE,
            Xlib.X.NONE,
            None)
        window.grab_button(LEFT_CLICK, 0, True,
            Xlib.X.ButtonReleaseMask | Xlib.X.ButtonPressMask,
            Xlib.X.GrabModeAsync,
            Xlib.X.GrabModeAsync,
            Xlib.X.NONE,
            Xlib.X.NONE,
            None)

    def handle_map_request(self, event):
        event.window.map()
        # if window is not focused:
        # event.window.ungrab(LEFT_CLICK, 0)
        # else
        self.grab_window_events(event.window)

    def handle_mapping_notify(self, event):
        self.wm.display.refresh_keyboard_mapping(event)

    def handle_mouse_motion(self, event):
        '''
        Click & drag to move window.
        '''
        if event.state & getMask(key_bindings.GRAB_BUTTON):
            self.wm.handle_window_drag(event.window, event.root_x, event.root_y)

    def handle_mouse_press(self, event):
        if event.detail == LEFT_CLICK:
            # Click: raise window
            event.window.configure(stack_mode=Xlib.X.Above)

    def handle_mouse_release(self, event):
        self.wm.drag_window = None

    def handle_key_press(self, event):
        if (event.state & key_bindings.MOD_KEY) and (event.detail in self.enter_codes):
            # Alt+Enter: start xterm
            system(XTERM_COMMAND)

    def redirect_screen_events(self, screen_id):
        '''
        Attempts to redirect the screen events, and returns True on success.
        '''
        # get root window
        root_window = self.wm.display.screen(screen_id).root

        error_catcher = Xlib.error.CatchError(Xlib.error.BadAccess)
        mask = Xlib.X.SubstructureRedirectMask
        root_window.change_attributes(event_mask=mask, onerror=error_catcher)

        self.wm.display.sync()
        error = error_catcher.get_error()
        if error:
            return False

        for code in self.enter_codes:
            # Grab Alt+Enter
            root_window.grab_key(code,
                key_bindings.MOD_KEY & ~RELEASE_MODIFIER,
                1,
                Xlib.X.GrabModeAsync,
                Xlib.X.GrabModeAsync)
        # Find all existing windows.
        for window in root_window.query_tree().children:
            print 'Grabbing mouse motion events for window {0}'.format(window)
            self.grab_window_events(window)
        return True

    def handle_key_release(self, event):
        pass

    def handle_configure_request(self, event):
        window = event.window
        args = { 'border_width': 1 }
        if event.value_mask & Xlib.X.CWX:
            args['x'] = event.x
        if event.value_mask & Xlib.X.CWY:
            args['y'] = event.y
        if event.value_mask & Xlib.X.CWWidth:
            args['width'] = event.width
        if event.value_mask & Xlib.X.CWHeight:
            args['height'] = event.height
        if event.value_mask & Xlib.X.CWSibling:
            args['sibling'] = event.above
        if event.value_mask & Xlib.X.CWStackMode:
            args['stack_mode'] = event.stack_mode
        window.configure(**args)
