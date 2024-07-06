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
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.label import Label

from os import listdir
from textwrap import fill
# Android **only** HTML viewer, always full screen.
#
# Back button or gesture has the usual browser behavior, except for the final
# back event which returns the UI to the view before the browser was opened.
#
# Base Class:  https://kivy.org/doc/stable/api-kivy.uix.modalview.html 
#
# Requires: android.permissions = INTERNET
# Uses:     orientation = landscape, portrait, or all
# Arguments:
# url               : required string,  https://   file:// (content://  ?) 
# enable_javascript : optional boolean, defaults False 
# enable_downloads  : optional boolean, defaults False 
# enable_zoom       : optional boolean, defaults False 
#
# Downloads are delivered to app storage see downloads_directory() below.
#
# Tested on api=27 and api=30
# 
# Note:
#    For api>27   http://  gives net::ERR_CLEARTEXT_NOT_PERMITTED 
#    This is Android implemented behavior.
#
# Source https://github.com/Android-for-Python/Webview-Example

from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from android.runnable import run_on_ui_thread
from jnius import autoclass, cast, PythonJavaClass, java_method

WebViewA = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
LinearLayout = autoclass('android.widget.LinearLayout')
KeyEvent = autoclass('android.view.KeyEvent')
ViewGroup = autoclass('android.view.ViewGroup')
DownloadManager = autoclass('android.app.DownloadManager')
DownloadManagerRequest = autoclass('android.app.DownloadManager$Request')
Uri = autoclass('android.net.Uri')
Environment = autoclass('android.os.Environment')
Context = autoclass('android.content.Context')
PythonActivity = autoclass('org.kivy.android.PythonActivity')


class DownloadListener(PythonJavaClass):
    #https://stackoverflow.com/questions/10069050/download-file-inside-webview
    __javacontext__ = 'app'
    __javainterfaces__ = ['android/webkit/DownloadListener']

    @java_method('(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;J)V')
    def onDownloadStart(self, url, userAgent, contentDisposition, mimetype,
                        contentLength):
        mActivity = PythonActivity.mActivity 
        context =  mActivity.getApplicationContext()
        visibility = DownloadManagerRequest.VISIBILITY_VISIBLE_NOTIFY_COMPLETED
        dir_type = Environment.DIRECTORY_DOWNLOADS
        uri = Uri.parse(url)
        filepath = uri.getLastPathSegment()
        request = DownloadManagerRequest(uri)
        request.setNotificationVisibility(visibility)
        request.setDestinationInExternalFilesDir(context,dir_type, filepath)
        dm = cast(DownloadManager,
                  mActivity.getSystemService(Context.DOWNLOAD_SERVICE))
        dm.enqueue(request)


class KeyListener(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['android/view/View$OnKeyListener']

    def __init__(self, listener):
        super().__init__()
        self.listener = listener

    @java_method('(Landroid/view/View;ILandroid/view/KeyEvent;)Z')
    def onKey(self, v, key_code, event):
        if event.getAction() == KeyEvent.ACTION_DOWN and\
           key_code == KeyEvent.KEYCODE_BACK: 
            return self.listener()
        

class WebView(ModalView):
    # https://developer.android.com/reference/android/webkit/WebView
    
    def __init__(self, url, enable_javascript = False, enable_downloads = False,
                 enable_zoom = False, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.enable_javascript = enable_javascript
        self.enable_downloads = enable_downloads
        self.enable_zoom = enable_zoom
        self.webview = None
        self.enable_dismiss = True
        self.open()

    @run_on_ui_thread        
    def on_open(self):
        mActivity = PythonActivity.mActivity 
        webview = WebViewA(mActivity)
        webview.setWebViewClient(WebViewClient())
        webview.getSettings().setJavaScriptEnabled(self.enable_javascript)
        webview.getSettings().setBuiltInZoomControls(self.enable_zoom)
        webview.getSettings().setDisplayZoomControls(False)
        webview.getSettings().setAllowFileAccess(True) #default False api>29
        layout = LinearLayout(mActivity)
        layout.setOrientation(LinearLayout.VERTICAL)
        layout.addView(webview, self.width, self.height)
        mActivity.addContentView(layout, LayoutParams(-1,-1))
        webview.setOnKeyListener(KeyListener(self._back_pressed))
        if self.enable_downloads:
            webview.setDownloadListener(DownloadListener())
        self.webview = webview
        self.layout = layout
        try:
            webview.loadUrl(self.url)
        except Exception as e:            
            print('Webview.on_open(): ' + str(e))
            self.dismiss()  
        
    @run_on_ui_thread        
    def on_dismiss(self):
        if self.enable_dismiss:
            self.enable_dismiss = False
            parent = cast(ViewGroup, self.layout.getParent())
            if parent is not None: parent.removeView(self.layout)
            self.webview.clearHistory()
            self.webview.clearCache(True)
            self.webview.clearFormData()
            self.webview.destroy()
            self.layout = None
            self.webview = None
        
    @run_on_ui_thread
    def on_size(self, instance, size):
        if self.webview:
            params = self.webview.getLayoutParams()
            params.width = self.width
            params.height = self.height
            self.webview.setLayoutParams(params)

    def pause(self):
        if self.webview:
            self.webview.pauseTimers()
            self.webview.onPause()

    def resume(self):
        if self.webview:
            self.webview.onResume()       
            self.webview.resumeTimers()

    def downloads_directory(self):
        # e.g. Android/data/org.test.myapp/files/Download
        dir_type = Environment.DIRECTORY_DOWNLOADS
        context =  PythonActivity.mActivity.getApplicationContext()
        directory = context.getExternalFilesDir(dir_type)
        return str(directory.getPath())

    def _back_pressed(self):
        if self.webview.canGoBack():
            self.webview.goBack()
        else:
            self.dismiss()  
        return True

        
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
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: 0.1
        TextInput:
            id: log_textinput
            readonly: False
            size_hint_y: None
            height: self.parent.height
            text: "127.0.0.1:8000"
            on_text: self.parent.scroll_y = 0 if len(self.text) > self.height else 1
        Button:
            id: gotowv
            height: '30dp'
            text: "URL"
            on_press: app.view_google(self)
    BoxLayout:
        id: wv
        orientation: "vertical"
'''

class MyKivyApp(App):
    def build(self):
        self.browser = None

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
        
        # Access the 'wv' widget using self.root.ids
        self.browser = self.root.ids.wv
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
      
    def view_google(self, instance):
        url = self.root.ids.log_textinput.text
        self.browser = WebView(url,
                               enable_javascript=True,
                               enable_downloads=True,
                               enable_zoom=True)


        
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
        if self.browser:
            self.browser.resume()
        # Resume reading log when the application is resumed
        if self.running:
            self.logging = True
            Clock.schedule_interval(self.read_stdout, 1.0)
    def handle_django_log(self, message):
        # Handle OSC messages received from Django server
        self.update_log(message.decode())
        
if __name__ == '__main__':
    MyKivyApp().run()

