import traceback

debug_on = True

def debug(value):
    if value:
        def decorate(f):
            def wrap(*args, **kwargs):
                try:
                    return f(*args,**kwargs)
                except Exception as e:
                    tb = traceback.format_exc()
                    sg.Print(f'An error happened.  Here is the info:', e, tb)
                    sg.popup_error(f'AN EXCEPTION OCCURRED!', e, tb)
            return wrap

        return decorate
    else:
        def decorate(f):
            def wrap(*args, **kwargs):
                return f(*args,**kwargs)
            return wrap