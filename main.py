from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
import os
from concurrent.futures import ThreadPoolExecutor, Future
try:
    from jnius import autoclass
except Exception:
    os.environ['JDK_HOME'] = "/usr/lib/jvm/openlogic-openjdk-8-hotspot-amd64"
    os.environ['JAVA_HOME'] = "/usr/lib/jvm/openlogic-openjdk-8-hotspot-amd64"
    from jnius import autoclass
from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer
import subprocess
import sys

# Set Java environment variables if running on Android
if platform == 'android':
    os.environ['JDK_HOME'] = "/usr/lib/jvm/openlogic-openjdk-8-hotspot-amd64"
    os.environ['JAVA_HOME'] = "/usr/lib/jvm/openlogic-openjdk-8-hotspot-amd64"

# Service name for Android (adjust as per your service class name)
SERVICE_NAME = u'{packagename}.{servicename}'.format(
    packagename=u'org.kivy.android',
    servicename=u'PythonService'
)

KV = '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: '30sp'
        Button:
            text: 'start service'
            on_press: app.start_service()
        Button:
            text: 'stop service'
            on_press: app.stop_service()
       

    ScrollView:
        Label:
            id: log_label
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.size[0], None

    BoxLayout:
        size_hint_y: None
        height: '30sp'
        Button:
            text: 'ping'
            on_press: app.send_ping()
        Button:
            text: 'clear'
            on_press: app.clear_log()
        Label:
            id: date

'''

class ClientServerApp(App):
    def build(self):
        self.service = None

        # Initialize OSC client and server
        self.server = server = OSCThreadServer()
        server.listen(
            address=b'localhost',
            port=8000,
            default=True,
        )
        server.bind(b'/message', self.display_message)
        server.bind(b'/date', self.date)
        server.bind(b'/django/log', self.display_log)  # Binding for Django log messages

        self.client = OSCClient(b'localhost', 8000)

        # Load Kivy GUI from KV string
        self.root = Builder.load_string(KV)
        return self.root

    def start_service(self):
        if platform == 'android':
            service = autoclass(SERVICE_NAME)
       
            self.mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            argument = ''
            service.start(self.mActivity, argument)
            self.service = service

        elif platform in ('linux', 'linux2', 'macos', 'win'):
            self.service = subprocess.Popen([sys.executable, 'manage.py', 'runserver', 'localhost:8000'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            Clock.schedule_interval(self.read_stdout, 0.1)  # Schedule reading stdout/stderr
        else:
            raise NotImplementedError("Service start not implemented on this platform")

    def read_stdout(self, dt):
        if self.service and hasattr(self.service, 'stdout'):
            output = self.service.stdout.readline()
            if output:
                # Send log message to Kivy
                self.display_log(output.decode('utf-8'))
        else:
            # Handle the case where self.service is None or doesn't have stdout
            # This might happen if service is not started yet or on Android
            pass

    def stop_service(self):
        if self.service:
            if platform == "android":
                self.service.stop(self.mActivity)
            elif platform in ('linux', 'linux2', 'macos', 'win'):
                if self.service and self.service.poll() is None:
                    self.service.terminate()  # Send termination signal
                    self.display_log("Django server stopped.\n")
         
            else:
                raise NotImplementedError("Service stop not implemented on this platform")
            self.service = None


    def send_ping(self):
        self.client.send_message(b'/ping', [])

    def clear_log(self):
        self.root.ids.log_label.text = ''

    def display_message(self, message):
        if self.root:
            self.root.ids.log_label.text += '{}\n'.format(message.decode('utf8'))

    def date(self, message):
        if self.root:
            self.root.ids.date.text = message.decode('utf8')

    def display_log(self, message):
        if self.root:
            self.root.ids.log_label.text += '{}\n'.format(message.strip())

if __name__ == '__main__':
    ClientServerApp().run()

