import os
import platform
import subprocess
from datetime import datetime
import win32gui

class Windows():

    def __init__(self) -> None:
        self.username = os.getlogin()
        self.os_platform = platform.system()
        self.os_version = platform.platform()
        self.session_time = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    def get_idle_time(self):
        try:
            idle_time_millis = int(subprocess.check_output(
                ["powershell", "-Command", "(Get-CimInstance Win32_ComputerSystem).CurrentTimeZone"]), text=True).split()[0]
            return idle_time_millis // 1000  # Convert to seconds
        except Exception as e:
            print(f"Error fetching idle time on Windows: {e}")
            return 0
    
    def get_active_application(self):
        try:
            window = win32gui.GetForegroundWindow()
            _window = win32gui.GetWindowText(window)
            app_name = _window.split('-')[-1].strip().replace(".","")  # Extract app name from window title
            window_title = _window.split('-')[0].strip()
            return app_name or "Unknown App", window_title or "Unknown Window"
        except Exception as e:
            print(f"Error fetching active window on Windows: {e}")
            return "Unknown App", "Unknown Window"