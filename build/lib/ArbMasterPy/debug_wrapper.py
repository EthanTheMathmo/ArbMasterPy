import traceback
import PySimpleGUI as sg


def debug_basic(value):
    if value:
        def decorate(f):
            def wrap(*args, **kwargs):
                try:
                    return f(*args,**kwargs)
                except Exception as e:
                    tb = traceback.format_exc()
                    sg.Print(f'An error happened.  Here is the info:', e, tb)
                    sg.popup_error(f'An exception has occured.', e, tb)
            return wrap

        return decorate
    else:
        def decorate(f):
            def wrap(*args, **kwargs):
                return f(*args,**kwargs)
            return wrap

