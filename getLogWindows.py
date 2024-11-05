import os
import platform
import subprocess
from datetime import datetime


class Windows():

    def __init__(self) -> None:
        self.username = os.getlogin()
        self.os_platform = platform.system()
        self.os_version = platform.platform()
        self.session_time = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    def get_idle_time_windows():
        try:
            idle_time_millis = int(subprocess.check_output(
                ["powershell", "-Command", "(Get-CimInstance Win32_ComputerSystem).CurrentTimeZone"]), text=True).split()[0]
            return idle_time_millis // 1000  # Convert to seconds
        except Exception as e:
            print(f"Error fetching idle time on Windows: {e}")
            return 0
    
    def get_active_application_window_windows():
        try:
            import win32gui
            window = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(window)
            app_name = window_title.split('-')[0].strip()  # Extract app name from window title
            return app_name, window_title
        except Exception as e:
            print(f"Error fetching active window on Windows: {e}")
            return None, None