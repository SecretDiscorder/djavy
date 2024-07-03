# main.py

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from android import AndroidService
from threading import Thread
from time import sleep

HERE = os.path.abspath(os.path.dirname(__file__))
LOGPATH = os.path.join(HERE, "djandro.log")

class DjandroApp(App):
    def build(self):
        self.service = AndroidService('Django', 'Django is running')
        open(LOGPATH, 'w').close()  # Touch the logfile
        self.layout = BoxLayout(orientation='vertical')

        self.info_label = Label(text="[color=#ff0000]Django is OFF[/color]", markup=True)
        self.layout.add_widget(self.info_label)

        self.btn = Button(text="Start Django")
        self.btn.bind(on_press=self.toggle)
        self.layout.add_widget(self.btn)

        self.console_label = Label(text="", markup=True)
        self.layout.add_widget(self.console_label)

        return self.layout

    def toggle(self, instance):
        if self.service.is_running():
            self.stop()
        else:
            self.start()

    def start(self):
        self.service.start(LOGPATH)
        self.start_logging()
        self.info_label.text = "[color=#00ff00]Django is ON[/color]"
        self.btn.text = "Stop Django"

    def stop(self):
        self.service.stop()
        self.logging = False
        self.info_label.text = "[color=#ff0000]Django is OFF[/color]"
        self.btn.text = "Start Django"

    def start_logging(self):
        self.logging = True
        Clock.schedule_interval(self.update_log, 0.5)

    def update_log(self, dt):
        with open(LOGPATH, 'r') as log_file:
            self.console_label.text = log_file.read()

    def on_pause(self):
        return True

    def on_resume(self):
        if self.service.is_running():
            self.start_logging()

if __name__ == '__main__':
    DjandroApp().run()

