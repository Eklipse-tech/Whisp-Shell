import os
import sys
import time
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
        # This is the "Container" that holds your app
        self.layout = BoxLayout(orientation='vertical')
        
        # Minimalist Loading Screen (Whisp Branding)
        self.label = Label(
            text="Whisp", 
            font_size='30sp', 
            color=(1, 1, 1, 0.5), # Faded white
            halign="center"
        )
        self.layout.add_widget(self.label)
        return self.layout

    def on_start(self):
        if platform == 'android':
            perms = [
                Permission.CAMERA, 
                Permission.RECORD_AUDIO,
                Permission.ACCESS_FINE_LOCATION, 
                Permission.READ_CONTACTS
            ]
            request_permissions(perms, self.perm_callback)
        else:
            self.update_app(0)

    def on_stop(self):
        # FORCE KILL: Stops battery drain when you swipe the app away
        sys.exit(0)

    def perm_callback(self, permissions, grants):
        # Instantly proceed to download
        Clock.schedule_once(self.update_app, 0.5)

    def update_app(self, dt):
        storage = self.user_data_dir if platform == 'android' else os.getcwd()
        file_path = os.path.join(storage, LOCAL_FILE)
        
        # 1. DOWNLOAD (Aggressive Cache Busting)
        try:
            # We add a random number to the URL so the phone NEVER uses an old version
            final_url = f"{UPDATE_URL}?t={int(time.time())}"
            
            # We use strict headers to force a fresh copy
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate', 
                'Pragma': 'no-cache', 
                'Expires': '0'
            }
            
            r = requests.get(final_url, headers=headers, timeout=5)
            
            if r.status_code == 200:
                with open(file_path, "w", encoding='utf-8') as f:
                    f.write(r.text)
                # Success - silent transition
            else:
                self.label.text = "Connection Error. Loading Offline..."
        except:
            pass # Silent fail to offline mode

        # 2. LAUNCH
        if os.path.exists(file_path):
            self.launch_dynamic_app(file_path)
        else:
            self.label.text = "Error: No Internet & No Saved App."

    def launch_dynamic_app(self, path):
        """
        Safely executes the downloaded code and attaches it to the screen.
        """
        try:
            with open(path, "r", encoding='utf-8') as f:
                code_content = f.read()
            
            # Wipe the "Whisp" loading text so the screen is clean
            self.layout.clear_widgets()
            
            # --- CRITICAL FIX ---
            # We pass 'app_instance' into the script so it can find the window
            global_vars = globals()
            local_vars = {'app_instance': self}
            
            exec(code_content, global_vars, local_vars)
            
            # Final check: If screen is empty, the downloaded code is buggy
            if not self.layout.children:
                self.layout.add_widget(Label(
                    text="Error: App loaded but screen is blank.\nCheck app.py code.", 
                    color=(1, 0, 0, 1)
                ))

        except Exception as e:
            # If the downloaded code crashes, show us why
            self.layout.clear_widgets()
            self.layout.add_widget(Label(
                text=f"CRASH: {str(e)}", 
                color=(1, 0, 0, 1), 
                halign="center"
            ))

if __name__ == '__main__':
    WhispShell().run()
