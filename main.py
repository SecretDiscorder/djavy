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
        self.btn.bind(on_press=self.toggle)
        self.layout.add_widget(self.btn)

        self.console_label = Label(text="", markup=True)
        self.layout.add_widget(self.console_label)

        self.service = AndroidService('Django', 'Django is running')
        open(LOGPATH, 'w').close()  # Touch the logfile

        self.service_running = False  # Track service state

        return self.layout



    def toggle(self):
        action = self.stop if self.running else self.start
        self.running = not self.running
        action()
        self.root.ids['info'].text = "[color=#ff0000]Django is OFF[/color]"
        if self.running:
            self.root.ids['info'].text = "[color=#00ff00]Django is ON[/color]"

        btn_text = 'Stop' if self.running else 'Start'
        self.root.ids['btn'].text = btn_text + " Django"

    def start(self):
        self.service.start(LOGPATH)
        self.start_logging()

    def stop(self):
        self.service.stop()
        self.logging = False
        self.running = False

    def start_logging(self):
        self.console = Thread(target=self.logger)
        self.logging = True
        self.console.start()

    def logger(self):
        label = self.root.ids['console']
        log = open(LOGPATH, 'r')
        label.text = log.read()
        while self.logging:
            log.seek(log.tell())
            label.text += log.read()
            sleep(0.2)

    def on_pause(self):
        if self.logging:
            self.logging = False
            self.console.join()
        return True


    def on_resume(self):
        if self.running:
            self.start_logging()

if __name__ == '__main__':
    DjandroApp().run()

