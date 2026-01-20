import os
import sys
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform
from android.permissions import request_permissions, Permission

# --- CONFIGURATION ---
# Your exact URL
UPDATE_URL = "https://raw.githubusercontent.com/Eklipse-tech/Whisp-Source/refs/heads/main/app.py"
LOCAL_FILE = "app_logic.py"

class WhispShell(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="[ Whisp Shell v2 ]\nConnecting...", halign="center")
        self.layout.add_widget(self.label)
        return self.layout

    def on_start(self):
        # Android Permissions
        if platform == 'android':
            perms = [
                Permission.CAMERA, 
                Permission.RECORD_AUDIO,
                Permission.ACCESS_FINE_LOCATION, 
                Permission.READ_CONTACTS
            ]
            request_permissions(perms, self.perm_callback)
        else:
            # PC Debugging
            self.update_app(0)

    def on_stop(self):
        # FORCE KILL: Ensures the app doesn't run in the background
        sys.exit(0)

    def perm_callback(self, permissions, grants):
        # Proceed regardless of permission results
        self.label.text = "Permissions Checked.\nDownloading..."
        Clock.schedule_once(self.update_app, 1)

    def update_app(self, dt):
        storage = self.user_data_dir if platform == 'android' else os.getcwd()
        file_path = os.path.join(storage, LOCAL_FILE)
        
        # 1. DOWNLOAD (Aggressive No-Cache)
        try:
            # Random query param (?t=...) tricks the server into thinking it's a new request
            # This PREVENTS you from having to "Clear Data" to see updates.
            import time
            final_url = f"{UPDATE_URL}?t={int(time.time())}"
            
            headers = {'Cache-Control': 'no-cache, no-store, must-revalidate'}
            r = requests.get(final_url, headers=headers, timeout=10)
            
            if r.status_code == 200:
                with open(file_path, "w", encoding='utf-8') as f:
                    f.write(r.text)
                self.label.text = "Update Downloaded!\nLaunching..."
            else:
                self.label.text = f"Server Error {r.status_code}. Using saved version..."
        except Exception as e:
            self.label.text = f"Offline Mode.\nUsing saved version..."

        # 2. LAUNCH
        if os.path.exists(file_path):
            self.launch_dynamic_app(file_path)
        else:
            self.label.text = "CRITICAL ERROR: No App Code Found!\nCheck Internet."

    def launch_dynamic_app(self, path):
        """
        Safely executes the downloaded code and attaches it to the screen.
        """
        try:
            with open(path, "r", encoding='utf-8') as f:
                code_content = f.read()
            
            # Wipe the "Loader" text
            self.layout.clear_widgets()
            
            # --- THE MAGIC FIX FOR BLACK SCREEN ---
            # We explicitly pass 'app_instance' so the script can find us
            # We use the current global scope to ensure imports work
            global_vars = globals()
            local_vars = {'app_instance': self}
            
            exec(code_content, global_vars, local_vars)
            
            # --- DIAGNOSTIC CHECK ---
            # If the screen is STILL empty after running the code, warn the user.
            if not self.layout.children:
                self.layout.add_widget(Label(
                    text="WARNING: Script loaded but screen is empty.\nDid you forget 'app_instance.layout.add_widget()'?", 
                    halign="center",
                    color=(1, 1, 0, 1) # Yellow Warning
                ))

        except Exception as e:
            # If the script crashes, SHOW THE ERROR IN RED
            self.layout.clear_widgets()
            self.layout.add_widget(Label(
                text=f"SCRIPT CRASH:\n{str(e)}", 
                color=(1, 0, 0, 1), # Red Error
                halign="center"
            ))

if __name__ == '__main__':
    WhispShell().run()
