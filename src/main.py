"""Main entry point for Stay-On-Track application."""

import signal
import sys
import threading
import time

import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as menu_item

from analytics_ui import AnalyticsWindow
from config import ConfigManager
from goals.gamification import GamificationManager
from goals.goal_manager import GoalManager
from goals.goal_setup_ui import GoalSetupWindow
from scheduler import Scheduler
from storage import StorageManager
from ui import HistoryWindow, InputWindow, SettingsWindow

try:
    from version import __version__
except ImportError:
    __version__ = "1.0.0"


def create_image(width, height, color1, color2):
    """Create a simple icon image."""
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image


class StayOnTrackApp(ctk.CTk):  # pylint: disable=too-many-instance-attributes
    """Main application class."""

    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("Stay On Track Helper")

        # Managers
        self.config_manager = ConfigManager()
        self.storage_manager = StorageManager(self.config_manager.get("output_dir"))
        self.goal_manager = GoalManager(self.storage_manager)
        self.gamification_manager = GamificationManager(self.storage_manager)

        # Check for and perform CSV migration on first launch
        self._check_migration()

        # Check for first-time goal setup
        self._check_first_time_setup()

        # Scheduler
        self.scheduler = Scheduler(self.config_manager, self.trigger_popup)
        self.scheduler.start()

        # State
        self.popup_window = None
        self.settings_window = None
        self.history_window = None
        self.analytics_window = None
        self.next_run_str = "Calculating..."

        # Tray Icon
        self.icon_image = create_image(64, 64, "black", "green")

        # Get version
        try:
            version_text = f"v{__version__}"
        except NameError:
            version_text = "v1.0.0"

        self.menu = pystray.Menu(
            menu_item(lambda text: self.next_run_str, lambda: None, enabled=False),
            menu_item(lambda text: version_text, lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            menu_item("Log Activity", self.trigger_popup),
            menu_item("Show History", self.open_history),
            menu_item("Analytics (Multi-Day)", self.open_analytics),
            menu_item("Settings", self.open_settings),
            menu_item("Exit", self.quit_app),
        )
        self.icon = pystray.Icon("name", self.icon_image, "Stay On Track", self.menu)

        self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.tray_thread.start()

        # Update loop for "Next: ..." label
        self.update_thread = threading.Thread(target=self._update_tray_label_loop, daemon=True)
        self.update_thread.start()

    def _check_migration(self):
        """Check if CSV migration is needed and perform it."""
        if self.storage_manager.needs_migration():
            print("Migrating existing CSV data to SQLite database...")
            count = self.storage_manager.migrate_from_csv()
            if count > 0:
                # Show notification after UI is ready
                self.after(1000, lambda: self._show_migration_notification(count))

    def _check_first_time_setup(self):
        """Check if this is first launch and show goal setup if needed."""
        if not self.goal_manager.has_any_goals():
            # First time - show goal setup
            self.after(500, self._show_goal_setup)  # Small delay to let app initialize

    def _show_goal_setup(self):
        """Show the first-time goal setup wizard."""
        setup_window = GoalSetupWindow(
            self.goal_manager, on_complete_callback=self._goal_setup_complete
        )
        setup_window.lift()
        setup_window.focus_force()

    def _goal_setup_complete(self):
        """Handle completion of goal setup."""
        # Could show a welcome message or tutorial here
        pass

    def _show_migration_notification(self, count):
        """Show a notification about successful migration."""
        try:
            # Create a simple notification window
            notification = ctk.CTkToplevel(self)
            notification.title("Migration Complete")
            notification.geometry("350x120")
            notification.attributes("-topmost", True)
            notification.resizable(False, False)

            # Center on screen
            notification.update_idletasks()
            x = (notification.winfo_screenwidth() - 350) // 2
            y = (notification.winfo_screenheight() - 120) // 2
            notification.geometry(f"350x120+{x}+{y}")

            # Message
            msg = ctk.CTkLabel(
                notification,
                text=f"Successfully migrated {count} entries\nfrom CSV files to SQLite database.",
                font=("Arial", 12),
            )
            msg.pack(pady=15)

            # OK button
            btn = ctk.CTkButton(notification, text="OK", width=80, command=notification.destroy)
            btn.pack(pady=10)

            notification.lift()
            notification.focus_force()
        except Exception as e:
            print(f"Could not show migration notification: {e}")

    def _update_tray_label_loop(self):
        """Update the tray menu label with next scheduled time."""
        while True:
            if self.scheduler.next_run_time:
                next_time = self.scheduler.next_run_time.strftime("%H:%M")
                self.next_run_str = f"Next: {next_time}"
                self.icon.update_menu()
            time.sleep(5)

    def trigger_popup(self):
        """Trigger the activity logging popup."""
        try:
            import winsound  # pylint: disable=import-outside-toplevel

            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except ImportError:
            pass
        self.after(0, self._show_popup_internal)

    def _show_popup_internal(self):
        """Show the popup window (internal method)."""
        if self.popup_window is None or not self.popup_window.winfo_exists():
            self.popup_window = InputWindow(
                self.storage_manager,
                self.goal_manager,
                self.gamification_manager,
                on_close_callback=self._popup_closed,
            )
            self.popup_window.lift()
            self.popup_window.focus_force()
        else:
            self.popup_window.lift()
            self.popup_window.focus_force()

    def _popup_closed(self):
        """Handle popup window close."""
        self.popup_window = None

    def open_settings(self):
        """Open the settings window."""
        self.after(0, self._show_settings_internal)

    def _show_settings_internal(self):
        """Show the settings window (internal method)."""
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(
                self.config_manager, on_save_callback=self._settings_saved
            )
            self.settings_window.lift()
            self.settings_window.focus_force()
        else:
            self.settings_window.lift()

    def open_history(self):
        """Open the history window."""
        self.after(0, self._show_history_internal)

    def _show_history_internal(self):
        """Show the history window (internal method)."""
        if self.history_window is None or not self.history_window.winfo_exists():
            self.history_window = HistoryWindow(self.storage_manager)
            self.history_window.lift()
            self.history_window.focus_force()
        else:
            self.history_window.lift()

    def open_analytics(self):
        """Open the analytics window."""
        self.after(0, self._show_analytics_internal)

    def _show_analytics_internal(self):
        """Show the analytics window (internal method)."""
        if self.analytics_window is None or not self.analytics_window.winfo_exists():
            self.analytics_window = AnalyticsWindow(self.storage_manager)
            self.analytics_window.lift()
            self.analytics_window.focus_force()
        else:
            self.analytics_window.lift()

    def _settings_saved(self):
        """Handle settings saved callback."""
        pass

    def quit_app(self, icon=None, _item=None):
        """Quit the application."""
        self.scheduler.stop()
        if icon:
            icon.stop()
        self.quit()
        sys.exit()


if __name__ == "__main__":
    import ctypes

    # Create a named mutex to ensure only one instance runs
    mutex_name = "Global\\StayOnTrackAppMutex"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()

    if last_error == 183:  # ERROR_ALREADY_EXISTS
        print("Stay On Track is already running.")
        sys.exit(0)

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = StayOnTrackApp()
    signal.signal(signal.SIGINT, lambda s, f: app.quit_app())
    app.mainloop()
