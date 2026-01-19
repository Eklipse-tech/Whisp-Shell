import os
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform
from android.permissions import request_permissions, Permission

# !!! REPLACE THIS WITH YOUR OTHER REPO'S RAW URL !!!
UPDATE_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/Whisp-Source/main/app.py"
LOCAL_FILE = "app_logic.py"

class WhispShell(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="[ Whisp Shell ]\nInitializing...", halign="center")
        self.layout.add_widget(self.label)
        return self.layout

    def on_start(self):
        if platform == 'android':
            perms = [
                Permission.INTERNET, Permission.CAMERA, Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE,
                Permission.ACCESS_FINE_LOCATION, Permission.READ_CONTACTS
            ]
            request_permissions(perms, self.perm_callback)
        else:
            self.update_app(0)

    def perm_callback(self, permissions, grants):
        if all(grants):
            self.label.text = "Permissions Granted.\nConnecting..."
            Clock.schedule_once(self.update_app, 1)
        else:
            self.label.text = "Error: Permissions Denied."

    def update_app(self, dt):
        storage = self.user_data_dir if platform == 'android' else os.getcwd()
        file_path = os.path.join(storage, LOCAL_FILE)
        try:
            # Force download without caching
            headers = {'Cache-Control': 'no-cache'}
            r = requests.get(UPDATE_URL, headers=headers, timeout=10)
            if r.status_code == 200:
                with open(file_path, "w") as f:
                    f.write(r.text)
                self.label.text = "Update Found! Launching..."
            else:
                self.label.text = "Server Error. Using cache..."
        except:
            self.label.text = "Offline. Using cache..."

        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    code = f.read()
                exec(code, globals(), {'app_instance': self})
            except Exception as e:
                self.label.text = f"CRASH: {e}"
        else:
            self.label.text = "No App Code Found!"

if __name__ == '__main__':
    WhispShell().run()
