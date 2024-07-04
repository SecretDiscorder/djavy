# mykivyapp.py

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.utils import platform
import os
import subprocess
import sys
from kivy.clock import Clock


HERE = os.path.abspath(os.path.dirname(__file__))
LOGPATH = os.path.join(HERE, "djandro.log")

if platform == 'android':
    from android.runnable import run_on_ui_thread

Builder.load_file('djandro.kv')  # Load the kv file

SERVICE_NAME = u'org.kivy.android.PythonService'
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
                Label:
                        id: log_label
                        size_hint_y: None
                        height: self.texture_size[1]
                        text_size: self.size[0], None


'''
class MyKivyApp(App):
    def build(self):
        self.service = None
        open(LOGPATH, 'w').close()  # Touch the logfile
        self.running = False
        self.logging = False
 # Load Kivy GUI from KV string
        self.root = Builder.load_string(KV)
        return self.root
# BoxLayout will be loaded from the .kv file

    if platform == 'android':
        @run_on_ui_thread
        def start_django_server(self, instance):
            try:
                python_executable = sys.executable
                self.django_process = subprocess.Popen(
                    [python_executable, 'manage.py', 'runserver', 'localhost:8000'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True  # Decode stdout as text
                )
                self.running = True
                Clock.schedule_interval(self.read_stdout, 0.1)  # Start reading stdout
            except Exception as e:
                print(f"Error starting Django server: {e}")

        @run_on_ui_thread
        def stop_django_server(self, instance):
            if hasattr(self, 'django_process') and self.django_process.poll() is None:
                self.django_process.terminate()
                self.running = False
                Clock.unschedule(self.read_stdout)
                print("Django server stopped.")
            else:
                print("Django server is not running.")
    else:
        def start_django_server(self, instance):
            try:
                python_executable = sys.executable
                self.django_process = subprocess.Popen(
                    [python_executable, 'manage.py', 'runserver', 'localhost:8001'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True  # Decode stdout as text
                )
                self.running = True
                Clock.schedule_interval(self.read_stdout, 0.1)  # Start reading stdout
            except Exception as e:
                print(f"Error starting Django server: {e}")

        def stop_django_server(self, instance):
            if hasattr(self, 'django_process') and self.django_process.poll() is None:
                self.running = False
                Clock.unschedule(self.read_stdout)
                self.django_process.terminate()
                print("Django server stopped.")
            else:
                print("Django server is not running.")
    def read_stdout(self, dt):
        if self.django_process and hasattr(self.django_process, 'stdout'):
            output = self.django_process.stdout.readline()
            if output:
                # Append new log message to existing text
                self.root.ids.log_label.text += output
                # Scroll to the bottom of the ScrollView
                self.root.ids.log_label.parent.scroll_y = 0
        else:
            # Handle the case where self.django_process is None or doesn't have stdout
            # This might happen if the process is not started yet or has terminated
            pass

if __name__ == '__main__':
    MyKivyApp().run()
