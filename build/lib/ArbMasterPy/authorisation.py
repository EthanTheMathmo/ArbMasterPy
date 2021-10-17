from hashlib import sha1
import PySimpleGUI as sg

user_name = "myretailsolutions"
our_key = user_name + "83IW4HRF0842892"
user_key = ""

def check_authentication():
    global product_authorised
    layout = [[sg.Text('Enter your authorisation code:')],
        [sg.Input()],
        [sg.OK()] ]
    window = sg.Window('Enter your authorisation code', layout)
    event, values = window.read()
    window.close()
    user_key = values[0]
    combined_key = our_key+user_key
    combined_key = bytes(combined_key, 'utf-8')
    sha1(combined_key).hexdigest()
    if sha1(combined_key).hexdigest() == 'f20e7d611306c25b412698ab2e4df0be85883f5d':
        product_authorised = True
    else:
        product_authorised = False


def authenticate(func):
    def authenticate_and_call(*args, **kwargs):
        if not product_authorised:
            raise Exception('Authentication Failed.')
        return func(*args, **kwargs)
    return authenticate_and_call
