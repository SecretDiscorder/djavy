import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock

from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler, get_internal_wsgi_application
from django.conf import settings
import sys

# Determine the storage path based on the platform
if platform == 'android':
    from android.storage import app_storage_path
    from android import mActivity
    context = mActivity.getApplicationContext()
    result = context.getExternalFilesDir(None)
    if result:
        STORAGE_PATH = result.getAbsolutePath()
    else:
        STORAGE_PATH = app_storage_path()  # Fallback, not as secure
else:
    STORAGE_PATH = os.path.abspath(os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings")

KV = '''
BoxLayout:
    orientation: 'vertical'
    Button:
        text: 'Start Django Server'
        size_hint_y: None
        height: '50dp'
        on_press: app.start_django_server(self)
    Button:
        text: 'Stop Django Server'
        size_hint_y: None
        height: '50dp'
        on_press: app.stop_django_server(self)
    ScrollView:
        TextInput:
            id: log_textinput
            readonly: True
            size_hint_y: None
            height: self.parent.height
            text: ""
            on_text: self.parent.scroll_y = 0 if len(self.text) > self.height else 1
'''

class MyKivyApp(App):
    def build(self):
        self.log_path = os.path.join(STORAGE_PATH, "djandro.log")
        open(self.log_path, 'w').close()  # Touch the logfile
        self.running = False
        self.logging = False
        self.root = Builder.load_string(KV)
        return self.root

    def start_django_server(self, instance):
        try:
            server_address = ('127.0.0.1', 8000)
            wsgi_handler = get_internal_wsgi_application()

            class CustomRequestHandler(WSGIRequestHandler):
                def log_message(self, format, *args):
                    msg = "[%s] %s" % (self.log_date_time_string(), format % args)
                    log_path = getattr(settings, 'LOG_PATH', None)
                    if log_path:
                        with open(log_path, 'a') as fh:
                            fh.write(msg + '\n')
                            fh.flush()
                        self.update_log(msg)
                    else:
                        # Handle the case where LOG_PATH is not defined in settings
                        pass
                def update_log(self, message):
                    # Access update_log method from MyKivyApp instance
                    self.server.app.update_log(message)

            self.httpd = WSGIServer(server_address, RequestHandler)
            self.httpd.set_app(wsgi_handler)
            self.httpd.serve_forever()
            self.running = True
            Clock.schedule_interval(self.read_stdout, 0.1)
        except Exception as e:
            print(f"Error starting Django server: {e}")

    def stop_django_server(self, instance):
        try:
            if hasattr(self, 'httpd'):
                self.httpd.shutdown()
                self.httpd.server_close()
                self.running = False
                Clock.unschedule(self.read_stdout)
                print("Django server stopped.")
            else:
                print("Django server is not running.")
        except Exception as e:
            print(f"Error stopping Django server: {e}")

    def update_log(self, message):
        # Update the TextInput with the new log message
        self.root.ids.log_textinput.text += message + '\n'
        # Automatically scroll to the bottom of the log
        self.root.ids.log_textinput.scroll_y = 0

    def read_stdout(self, dt):
        # Method to read stdout from Django process if needed
        pass

if __name__ == '__main__':
    MyKivyApp().run()

