"""UI components for the Stay-On-Track application."""

import datetime
import os
import subprocess
import customtkinter as ctk

class InputWindow(ctk.CTkToplevel):
    """Window for logging user activity entries."""
    def __init__(self, storage_manager, on_close_callback=None):
        super().__init__()
        self.storage_manager = storage_manager
        self.on_close_callback = on_close_callback

        self.title("Stay On Track - Log Activity")
        self.geometry("400x200")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Label
        self.label = ctk.CTkLabel(self, text="What have you worked on?", font=("Arial", 14))
        self.label.pack(pady=10)

        # Entry
        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.submit)
        self.entry.focus_set()

        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.submit_btn = ctk.CTkButton(self.btn_frame, text="Save", command=self.submit)
        self.submit_btn.pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def submit(self, _event=None):
        """Submit the activity entry and close the window."""
        comment = self.entry.get().strip()
        if comment:
            self.storage_manager.save_entry(comment)
        self.on_close()

    def on_close(self):
        """Handle window close event."""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

class SettingsWindow(ctk.CTkToplevel):
    """Window for configuring application settings."""
    def __init__(self, config_manager, on_save_callback=None):
        super().__init__()
        self.config_manager = config_manager
        self.on_save_callback = on_save_callback

        self.title("Settings")
        self.geometry("300x250")
        self.attributes("-topmost", True)

        self._create_widgets()
        self._load_current_values()

    def _create_widgets(self):
        # Time Window
        self.lbl_start = ctk.CTkLabel(self, text="Start Time (HH:MM)")
        self.lbl_start.pack(pady=5)
        self.ent_start = ctk.CTkEntry(self)
        self.ent_start.pack(pady=5)

        self.lbl_end = ctk.CTkLabel(self, text="End Time (HH:MM)")
        self.lbl_end.pack(pady=5)
        self.ent_end = ctk.CTkEntry(self)
        self.ent_end.pack(pady=5)

        # Save Button
        self.btn_save = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.btn_save.pack(pady=20)

    def _load_current_values(self):
        self.ent_start.insert(0, self.config_manager.get("start_time"))
        self.ent_end.insert(0, self.config_manager.get("end_time"))

    def save_settings(self):
        """Save the updated settings and close the window."""
        new_config = {
            "start_time": self.ent_start.get().strip(),
            "end_time": self.ent_end.get().strip()
        }
        self.config_manager.save_config(new_config)

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()

class HistoryWindow(ctk.CTkToplevel):
    """Window for viewing activity history with date navigation."""
    def __init__(self, storage_manager):
        super().__init__()
        self.storage_manager = storage_manager
        self.current_date = datetime.date.today()
        self.title("Activity Log")
        self.geometry("500x600")
        self.attributes("-topmost", True)

        # Title with date
        self.lbl_title = ctk.CTkLabel(
            self,
            text=self._format_title(),
            font=("Arial", 16, "bold")
        )
        self.lbl_title.pack(pady=10)

        # Navigation Frame
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=5)

        # Store buttons in dictionary to reduce instance attributes
        self.nav_buttons = {}

        # Previous Day Button
        self.nav_buttons['prev'] = ctk.CTkButton(
            nav_frame,
            text="◀ Prev",
            width=80,
            command=self._prev_day
        )
        self.nav_buttons['prev'].pack(side="left", padx=5)

        # Today Button
        self.nav_buttons['today'] = ctk.CTkButton(
            nav_frame,
            text="Today",
            width=80,
            command=self._goto_today
        )
        self.nav_buttons['today'].pack(side="left", padx=5)

        # Next Day Button
        self.nav_buttons['next'] = ctk.CTkButton(
            nav_frame,
            text="Next ▶",
            width=80,
            command=self._next_day
        )
        self.nav_buttons['next'].pack(side="left", padx=5)

        # Open Folder Button
        self.nav_buttons['folder'] = ctk.CTkButton(
            nav_frame,
            text="📁 Open Folder",
            width=120,
            command=self._open_folder
        )
        self.nav_buttons['folder'].pack(side="left", padx=5)

        # Scrollable Frame for items
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=480, height=450)
        self.scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self._load_entries()

    def _format_title(self):
        """Format title with current date"""
        if self.current_date == datetime.date.today():
            return f"Activity Log - Today ({self.current_date.strftime('%Y-%m-%d')})"
        return f"Activity Log - {self.current_date.strftime('%Y-%m-%d')}"

    def _prev_day(self):
        """Navigate to previous day"""
        self.current_date -= datetime.timedelta(days=1)
        self._refresh()

    def _next_day(self):
        """Navigate to next day"""
        # Don't allow future dates
        if self.current_date < datetime.date.today():
            self.current_date += datetime.timedelta(days=1)
            self._refresh()

    def _goto_today(self):
        """Jump to today"""
        self.current_date = datetime.date.today()
        self._refresh()

    def _open_folder(self):
        """Open the data folder in Windows Explorer"""
        folder_path = self.storage_manager.output_dir
        if os.path.exists(folder_path):
            with subprocess.Popen(
                f'explorer "{folder_path}"',
                shell=True
            ) as _:
                pass  # Process will run independently

    def _refresh(self):
        """Refresh the window with new date"""
        self.lbl_title.configure(text=self._format_title())

        # Clear existing entries
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self._load_entries()

    def _load_entries(self):
        """Load entries for current date"""
        entries = self.storage_manager.get_entries_for_date(self.current_date)

        if not entries:
            lbl = ctk.CTkLabel(
                self.scroll_frame,
                text=f"No entries for {self.current_date.strftime('%Y-%m-%d')}."
            )
            lbl.pack(pady=10)
            return

        # Show entry count
        count_lbl = ctk.CTkLabel(
            self.scroll_frame,
            text=f"📊 {len(entries)} entries",
            font=("Arial", 12, "bold"),
            text_color="gray"
        )
        count_lbl.pack(pady=5)

        # Reverse order to see latest first
        for entry in reversed(entries):
            # entry structure: [Timestamp, Comment]
            if len(entry) < 2:
                continue

            timestamp = entry[0]
            comment = entry[1]

            # Row Frame
            row_frame = ctk.CTkFrame(self.scroll_frame)
            row_frame.pack(pady=2, padx=5, fill="x")

            lbl_time = ctk.CTkLabel(
                row_frame,
                text=timestamp,
                text_color="gray",
                width=70,
                font=("Arial", 11)
            )
            lbl_time.pack(side="left", padx=5)

            lbl_comment = ctk.CTkLabel(
                row_frame,
                text=comment,
                anchor="w",
                wraplength=350
            )
            lbl_comment.pack(side="left", padx=5, fill="x", expand=True)
