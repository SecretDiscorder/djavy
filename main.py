from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from android import AndroidService
from jnius import autoclass, cast
import os
from time import sleep
from threading import Thread

HERE = os.path.abspath(os.path.dirname(__file__))
LOGPATH = os.path.join(HERE, "djandro.log")

class DjandroApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.info_label = Label(text="[color=#ff0000]Django is OFF[/color]", markup=True)
        self.layout.add_widget(self.info_label)

        self.btn = Button(text="Start Django")
        self.btn.bind(on_press=self.toggle)  # Binding toggle method to on_press event
        self.layout.add_widget(self.btn)

        self.console_label = Label(text="", markup=True)
        self.layout.add_widget(self.console_label)

        self.service = AndroidService('Django', 'Django is running')
        open(LOGPATH, 'w').close()  # Touch the logfile

        self.service_running = False  # Track service state

        return self.layout

    def toggle(self, instance):  # Adjusted to accept the instance argument
        action = self.stop if self.service_running else self.start
        self.service_running = not self.service_running
        action()
        
        if self.service_running:
            self.info_label.text = "[color=#00ff00]Django is ON[/color]"
            self.btn.text = "Stop Django"
        else:
            self.info_label.text = "[color=#ff0000]Django is OFF[/color]"
            self.btn.text = "Start Django"

    def start(self):
        self.service.start(LOGPATH)
        self.start_logging()

    def stop(self):
        self.service.stop()
        self.logging = False

    def start_logging(self):
        self.console_thread = Thread(target=self.logger)
        self.logging = True
        self.console_thread.start()

    def logger(self):
        while self.logging:
            with open(LOGPATH, 'r') as log_file:
                log_contents = log_file.read()
            self.console_label.text = log_contents
            sleep(0.5)

    def on_pause(self):
        if self.logging:
            self.logging = False
            self.console_thread.join()
        return True

    def on_resume(self):
        if self.service_running:
            self.start_logging()

if __name__ == '__main__':
    DjandroApp().run()
