
import threading
import sys
import os
import signal
import time
from PIL import Image, ImageDraw
import customtkinter as ctk
import pystray
from pystray import MenuItem as item

from config import ConfigManager
from storage import StorageManager
from ui import InputWindow, SettingsWindow, HistoryWindow
from scheduler import Scheduler

def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

class StayOnTrackApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("Stay On Track Helper")

        # Managers
        self.config_manager = ConfigManager()
        self.storage_manager = StorageManager(self.config_manager.get("output_dir"))
        
        # Scheduler
        self.scheduler = Scheduler(self.config_manager, self.trigger_popup)
        self.scheduler.start()

        # State
        self.popup_window = None
        self.settings_window = None
        self.history_window = None
        self.next_run_str = "Calculating..."

        # Tray Icon
        self.icon_image = create_image(64, 64, 'black', 'green')
        self.menu = pystray.Menu(
            item(lambda text: self.next_run_str, lambda: None, enabled=False),
            item('Log Activity', self.trigger_popup),
            item('Show History', self.open_history),
            item('Settings', self.open_settings),
            item('Exit', self.quit_app)
        )
        self.icon = pystray.Icon("name", self.icon_image, "Stay On Track", self.menu)
        
        self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.tray_thread.start()

        # Update loop for "Next: ..." label
        self.update_thread = threading.Thread(target=self._update_tray_label_loop, daemon=True)
        self.update_thread.start()

    def _update_tray_label_loop(self):
        while True:
            if self.scheduler.next_run_time:
                self.next_run_str = f"Next: {self.scheduler.next_run_time.strftime('%H:%M')}"
                self.icon.update_menu()
            time.sleep(5)

    def trigger_popup(self):
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except:
            pass
        self.after(0, self._show_popup_internal)

    def _show_popup_internal(self):
        if self.popup_window is None or not self.popup_window.winfo_exists():
            self.popup_window = InputWindow(self.storage_manager, on_close_callback=self._popup_closed)
            self.popup_window.lift()
            self.popup_window.focus_force()
        else:
            self.popup_window.lift()
            self.popup_window.focus_force()

    def _popup_closed(self):
        self.popup_window = None

    def open_settings(self):
        self.after(0, self._show_settings_internal)

    def _show_settings_internal(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self.config_manager, on_save_callback=self._settings_saved)
            self.settings_window.lift()
            self.settings_window.focus_force()
        else:
            self.settings_window.lift()

    def open_history(self):
        self.after(0, self._show_history_internal)

    def _show_history_internal(self):
        if self.history_window is None or not self.history_window.winfo_exists():
            self.history_window = HistoryWindow(self.storage_manager)
            self.history_window.lift()
            self.history_window.focus_force()
        else:
            self.history_window.lift()

    def _settings_saved(self):
        pass

    def quit_app(self, icon=None, item=None):
        self.scheduler.stop()
        if icon:
            icon.stop()
        self.quit()
        sys.exit()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = StayOnTrackApp()
    signal.signal(signal.SIGINT, lambda s, f: app.quit_app())
    app.mainloop()
