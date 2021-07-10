import eel
import sys
import socket

ENTRY_PINT = 'index.html'
CHROME_ARGS = [
    '--incognit',
    '--disable-http-cache',
    '--disable-plugins',
    '--disable-extensions',
    '--disable-dev-tools',
]
ALLOW_EXTENSIONS = ['.html','.css','.js','.ico']


def start(appName, endpoint, size):
    eel.init(appName, allowed_extensions=ALLOW_EXTENSIONS)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    options = {
        'mode': "chrome",
        'close_callback': exit,
        'port': port,
        'cmdline_args': CHROME_ARGS
    }
    eel.start(endpoint, options=options,
        size=size, suppress_error=True)

def exit(arg1, arg2):
    sys.exit(0)
    