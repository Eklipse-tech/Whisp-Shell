import os
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform
from android.permissions import request_permissions, Permission

# !!! MAKE SURE THIS LINK IS CORRECT !!!
UPDATE_URL = "https://raw.githubusercontent.com/Eklipse-tech/Whisp-Source/refs/heads/main/app.py"
LOCAL_FILE = "app_logic.py"

class WhispShell(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="[ Whisp Shell ]\nInitializing...", halign="center")
        self.layout.add_widget(self.label)
        return self.layout

    def on_start(self):
        if platform == 'android':
            # We removed STORAGE permissions because they cause bugs on Android 11+
            # Your app folder is private and safe to write to without them.
            perms = [
                Permission.CAMERA, 
                Permission.RECORD_AUDIO,
                Permission.ACCESS_FINE_LOCATION, 
                Permission.READ_CONTACTS
            ]
            request_permissions(perms, self.perm_callback)
        else:
            self.update_app(0)

    def perm_callback(self, permissions, grants):
        # We don't care if permissions are denied. We try to launch anyway.
        # The 'Shell' shouldn't be the police. 
        self.label.text = "Permissions Checked.\nConnecting..."
        Clock.schedule_once(self.update_app, 1)

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
                # Wipe the loader UI before running the new app
                self.layout.clear_widgets()
                exec(code, globals(), {'app_instance': self})
            except Exception as e:
                self.label.text = f"CRASH: {e}"
        else:
            self.label.text = "No App Code Found!"

if __name__ == '__main__':
    WhispShell().run()
