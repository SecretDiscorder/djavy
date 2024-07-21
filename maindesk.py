import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer
from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler, get_internal_wsgi_application
from django.conf import settings
import threading

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
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: 0.1

        Button:
            text: 'Start Server'
            size_hint_y: None
            height: '50dp'
            on_press: app.start_django_server(self)
        Button:
            text: 'Stop Server'
            size_hint_y: None
            height: '50dp'
            on_press: app.stop_django_server(self)
        Button:
            id: info
            size_hint_y: None
            height: '50dp'
            text: ""
            markup: True
    ScrollView:
        TextInput:
            id: log_textinput
            readonly: True
            size_hint_y: None
            height: self.parent.height
            text: "127.0.0.1:8000"
            on_text: self.parent.scroll_y = 0 if len(self.text) > self.height else 1
'''

class MyKivyApp(App):
    def build(self):
        self.log_path = os.path.join(STORAGE_PATH, "djandro.log")
        open(self.log_path, 'a').close()  # Touch the logfile
        self.running = False
        self.logging = False
        self.root = Builder.load_string(KV)
# Initialize OSC client and server
        self.osc_server = OSCThreadServer()
        self.osc_server.listen(address='127.0.0.1', port=3001, default=True)
        self.osc_client = OSCClient('127.0.0.1', port=3000)
        
        # Bind OSC handlers
        self.osc_server.bind(b'/django_log', self.handle_django_log)
        

        Clock.schedule_interval(self.read_stdout, 1.0)  # Update log every 1 second
        self.update_toggle_text()  
        return self.root
    def update_toggle_text(self):
        if self.running:
            self.root.ids.info.text = "[color=#00ff00]Django is ON[/color]"
        else:
            self.root.ids.info.text = "[color=#ff0000]Django is OFF[/color]"
    def start_django_server(self, instance):

        if not self.running:
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
                            Clock.schedule_once(lambda dt: self.update_log(msg))
                        else:
                            # Handle the case where LOG_PATH is not defined in settings
                            pass

                    def update_log(self, message):
                        # Access update_log method from MyKivyApp instance
                        self.server.app.update_log(message)

                def run_server():
                    self.httpd = WSGIServer(server_address, CustomRequestHandler)
                    self.httpd.set_app(wsgi_handler)
                    self.httpd.serve_forever()

                self.server_thread = threading.Thread(target=run_server)
                self.server_thread.daemon = True  # Daemonize thread to close with main application
                self.server_thread.start()
                self.running = True     
                self.update_toggle_text()  # Update toggle button text
                self.osc_client.send_message(b'/start_django', [])
                # Open webview window
                webbrowser.open('http://127.0.0.1:8000')
                print("Django server started.")
            except Exception as e:
                print(f"Error starting Django server: {e}")

    def stop_django_server(self, instance):
        if self.running:
            try:
                if hasattr(self, 'httpd'):
                    self.httpd.shutdown()
                    self.httpd.server_close()
                    self.running = False
                    self.osc_client.send_message(b'/stop_django', [])
                    self.update_toggle_text() 
                    print("Django server stopped.")
                else:
                    print("Django server is not running.")
            except Exception as e:
                print(f"Error stopping Django server: {e}")
        else:
            print("Django server is not running.")

    def update_log(self, message):
        # Clear existing text before updating
        self.root.ids.log_textinput.text = ""
        
        # Update the TextInput with the new log message
        self.root.ids.log_textinput.text += message + '\n'
        
        # Automatically scroll to the bottom of the log
        self.root.ids.log_textinput.scroll_y = 0
        
    def read_stdout(self, dt):
        try:
            with open(self.log_path, 'r') as log_file:
                msg = log_file.read().strip()
                if msg:
                    self.update_log(msg)
        except Exception as e:
            print(f"Error reading Django log file: {e}")
    def on_pause(self):
        # Pause reading log when the application is paused
        if self.logging:
            self.logging = False
        return True

    def on_resume(self):
        # Resume reading log when the application is resumed
        if self.running:
            self.logging = True
            Clock.schedule_interval(self.read_stdout, 1.0)
    def handle_django_log(self, message):
        # Handle OSC messages received from Django server
        self.update_log(message.decode())
        
if __name__ == '__main__':
    MyKivyApp().run()

