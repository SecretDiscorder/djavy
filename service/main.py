import os
from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler, get_internal_wsgi_application
from django.utils.termcolors import PALETTES

palette = PALETTES['dark']
COLOR_MAP = {
    'black': '000000',
    'red': 'ff0000',
    'green': '00ff00',
    'blue': '0000ff',
    'cyan': '00ffff',
    'magenta': 'ff00ff',
    'yellow': 'ffff00',
    'white': 'ffffff'
}

STYLE_MAP = {
    'bold': 'b',
    'italic': 'i'
}

def colorize(msg, style):
    style_dct = palette[style]
    color = style_dct.get('fg', None)
    if color is not None:
        msg = '[color=#' + COLOR_MAP[color] + ']' + msg + '[/color]'
    opts = style_dct.get('opts', [])
    for o in opts:
        msg = '[' + STYLE_MAP[o] + ']' + msg + '[/' + STYLE_MAP[o] + ']'
    return msg


def add_markup(msg, args):
    # Utilize terminal colors, if available
    if args[1][0] == '2':
        # Put 2XX first, since it should be the common case
        msg = colorize(msg, 'HTTP_SUCCESS')
    elif args[1][0] == '1':
        msg = colorize(msg, 'HTTP_INFO')
    elif args[1] == '304':
        msg = colorize(msg, 'HTTP_NOT_MODIFIED')
    elif args[1][0] == '3':
        msg = colorize(msg, 'HTTP_REDIRECT')
    elif args[1] == '404':
        msg = colorize(msg, 'HTTP_NOT_FOUND')
    elif args[1][0] == '4':
        msg = colorize(msg, 'HTTP_BAD_REQUEST')
    else:
        # Any 5XX, or any other response
        msg = colorize(msg, 'HTTP_SERVER_ERROR')
    return msg

logpath = os.getenv('PYTHON_SERVICE_ARGUMENT')


class RequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        # Don't bother logging requests for admin images, or the favicon.
        if (self.path.startswith(self.admin_static_prefix)
                or self.path == '/favicon.ico'):
            return

        msg = "[%s] %s" % (self.log_date_time_string(), format % args)
        kivymarkup = add_markup(msg, args)
        with open(logpath, 'a') as fh:
            fh.write(kivymarkup + '\n')
            fh.flush()

server_address = ('127.0.0.1', 8000)
wsgi_handler = get_internal_wsgi_application()
httpd = WSGIServer(server_address, RequestHandler)
httpd.set_app(wsgi_handler)
httpd.serve_forever()
