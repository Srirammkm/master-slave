import os
import platform
import subprocess
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
)
from Quartz import kCGWindowOwnerName, kCGWindowName
from datetime import datetime


class Mac:
    def __init__(self):
        self.username = os.getlogin()
        self.os_platform = platform.system()
        self.os_version = platform.platform()
        self.session_time = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    def get_idle_time(self):
        try:
            idle_time_millis = (
                int(
                    subprocess.check_output(["ioreg", "-c", "IOHIDSystem"], text=True)
                    .split('"HIDIdleTime" = ')[1]
                    .split()[0]
                )
                // 1000000000
            )
            return idle_time_millis
        except Exception as e:
            print(f"Error fetching idle time on macOS: {e}")
            return 0

    def get_active_application(self):
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        for window in window_list:
            if window.get(kCGWindowOwnerName) and window.get("kCGWindowLayer") == 0:
                app_name = window.get(kCGWindowOwnerName, "Unknown App")
                window_title = window.get(kCGWindowName, app_name)
                return app_name, window_title
        return "Unknown App", "Unknown Window"
