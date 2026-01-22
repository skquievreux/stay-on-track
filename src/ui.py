"""UI components for the Stay-On-Track application."""

import datetime
import os
import subprocess

import customtkinter as ctk


class InputWindow(ctk.CTkToplevel):
    """Window for logging user activity entries with optional effectiveness voting."""

    def __init__(self, storage_manager, on_close_callback=None):
        super().__init__()
        self.storage_manager = storage_manager
        self.on_close_callback = on_close_callback
        self.selected_effectiveness = None

        # Check if extended mode is needed (30+ min since last entry)
        self.show_extended = self._check_extended_mode()
        self.recent_entries = []

        if self.show_extended:
            self.recent_entries = storage_manager.get_recent_entries(limit=2)

        # Configure window
        self.title("Stay On Track - Log Activity")
        window_height = 350 if self.show_extended else 250
        self.geometry(f"450x{window_height}")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Build UI
        if self.show_extended:
            self._create_extended_ui()
        else:
            self._create_standard_ui()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _check_extended_mode(self):
        """Check if 30+ minutes have passed since last entry."""
        last_time = self.storage_manager.get_last_entry_time()
        if last_time is None:
            return False

        minutes_since = (datetime.datetime.now() - last_time).total_seconds() / 60
        return minutes_since > 30

    def _create_standard_ui(self):
        """Create the standard input UI."""
        # Label
        self.label = ctk.CTkLabel(self, text="What have you worked on?", font=("Arial", 14))
        self.label.pack(pady=10)

        # Entry
        self.entry = ctk.CTkEntry(self, width=350, height=35)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.submit)
        self.entry.focus_set()

        # Effectiveness section
        self._create_effectiveness_section()

        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=15)

        self.submit_btn = ctk.CTkButton(
            self.btn_frame, text="Save", command=self.submit, width=100, height=35
        )
        self.submit_btn.pack(side="left", padx=5)

    def _create_extended_ui(self):
        """Create the extended input UI with recent entries and effectiveness voting."""
        # Warning label
        warning_frame = ctk.CTkFrame(self, fg_color="#FFF3CD", corner_radius=8)
        warning_frame.pack(pady=10, padx=15, fill="x")

        warning_label = ctk.CTkLabel(
            warning_frame,
            text="30+ min since last entry!",
            font=("Arial", 12, "bold"),
            text_color="#856404",
        )
        warning_label.pack(pady=8)

        # Recent entries section
        if self.recent_entries:
            recent_frame = ctk.CTkFrame(self, fg_color="transparent")
            recent_frame.pack(pady=5, padx=15, fill="x")

            recent_label = ctk.CTkLabel(
                recent_frame, text="Recent entries (click to use):", font=("Arial", 11)
            )
            recent_label.pack(anchor="w", pady=(0, 5))

            for entry in self.recent_entries:
                timestamp = entry["timestamp"].strftime("%H:%M")
                activity = entry["activity"]
                # Truncate long activities
                display_text = (
                    f"{timestamp} - {activity[:40]}..."
                    if len(activity) > 40
                    else f"{timestamp} - {activity}"
                )

                entry_btn = ctk.CTkButton(
                    recent_frame,
                    text=display_text,
                    font=("Arial", 11),
                    fg_color="#E8E8E8",
                    text_color="#333333",
                    hover_color="#D0D0D0",
                    anchor="w",
                    height=30,
                    command=lambda a=activity: self._fill_entry(a),
                )
                entry_btn.pack(fill="x", pady=2)

        # Main input label
        self.label = ctk.CTkLabel(self, text="What have you worked on?", font=("Arial", 14))
        self.label.pack(pady=(15, 5))

        # Entry field
        self.entry = ctk.CTkEntry(self, width=350, height=35)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self.submit)
        self.entry.focus_set()

        # Effectiveness section
        self._create_effectiveness_section()

        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=15)

        self.submit_btn = ctk.CTkButton(
            self.btn_frame, text="Save", command=self.submit, width=100, height=35
        )
        self.submit_btn.pack(side="left", padx=5)

    def _create_effectiveness_section(self):
        """Create the effectiveness voting buttons."""
        eff_frame = ctk.CTkFrame(self, fg_color="transparent")
        eff_frame.pack(pady=10)

        eff_label = ctk.CTkLabel(eff_frame, text="How effective? (optional)", font=("Arial", 11))
        eff_label.pack(pady=(0, 8))

        btn_container = ctk.CTkFrame(eff_frame, fg_color="transparent")
        btn_container.pack()

        # Good button
        self.btn_good = ctk.CTkButton(
            btn_container,
            text="Good",
            width=100,
            height=35,
            fg_color="#E8F5E9",
            text_color="#2E7D32",
            hover_color="#C8E6C9",
            command=lambda: self._select_effectiveness("good"),
        )
        self.btn_good.pack(side="left", padx=10)

        # Bad button
        self.btn_bad = ctk.CTkButton(
            btn_container,
            text="Bad",
            width=100,
            height=35,
            fg_color="#FFEBEE",
            text_color="#C62828",
            hover_color="#FFCDD2",
            command=lambda: self._select_effectiveness("bad"),
        )
        self.btn_bad.pack(side="left", padx=10)

    def _select_effectiveness(self, value):
        """Handle effectiveness button selection."""
        # Toggle selection
        if self.selected_effectiveness == value:
            self.selected_effectiveness = None
            # Reset button colors
            self.btn_good.configure(fg_color="#E8F5E9")
            self.btn_bad.configure(fg_color="#FFEBEE")
        else:
            self.selected_effectiveness = value
            # Update button colors to show selection
            if value == "good":
                self.btn_good.configure(fg_color="#4CAF50")
                self.btn_bad.configure(fg_color="#FFEBEE")
            else:
                self.btn_good.configure(fg_color="#E8F5E9")
                self.btn_bad.configure(fg_color="#EF5350")

    def _fill_entry(self, activity):
        """Fill the entry field with a recent activity."""
        self.entry.delete(0, "end")
        self.entry.insert(0, activity)
        self.entry.focus_set()

    def submit(self, _event=None):
        """Submit the activity entry and close the window."""
        comment = self.entry.get().strip()
        if comment:
            self.storage_manager.save_entry(comment, self.selected_effectiveness)
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
            "end_time": self.ent_end.get().strip(),
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
        self.geometry("550x650")
        self.attributes("-topmost", True)

        # Title with date
        self.lbl_title = ctk.CTkLabel(self, text=self._format_title(), font=("Arial", 16, "bold"))
        self.lbl_title.pack(pady=10)

        # Navigation Frame
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=5)

        # Store buttons in dictionary to reduce instance attributes
        self.nav_buttons = {}

        # Previous Day Button
        self.nav_buttons["prev"] = ctk.CTkButton(
            nav_frame, text="Prev", width=80, command=self._prev_day
        )
        self.nav_buttons["prev"].pack(side="left", padx=5)

        # Today Button
        self.nav_buttons["today"] = ctk.CTkButton(
            nav_frame, text="Today", width=80, command=self._goto_today
        )
        self.nav_buttons["today"].pack(side="left", padx=5)

        # Next Day Button
        self.nav_buttons["next"] = ctk.CTkButton(
            nav_frame, text="Next", width=80, command=self._next_day
        )
        self.nav_buttons["next"].pack(side="left", padx=5)

        # Open Folder Button
        self.nav_buttons["folder"] = ctk.CTkButton(
            nav_frame, text="Open Folder", width=100, command=self._open_folder
        )
        self.nav_buttons["folder"].pack(side="left", padx=5)

        # Scrollable Frame for items
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=530, height=500)
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
            with subprocess.Popen(f'explorer "{folder_path}"', shell=True) as _:
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
                text=f"No entries for {self.current_date.strftime('%Y-%m-%d')}.",
            )
            lbl.pack(pady=10)
            return

        # Show entry count
        count_lbl = ctk.CTkLabel(
            self.scroll_frame,
            text=f"{len(entries)} entries",
            font=("Arial", 12, "bold"),
            text_color="gray",
        )
        count_lbl.pack(pady=5)

        # Reverse order to see latest first
        for entry in reversed(entries):
            # Entry is now a dict with keys: id, timestamp, activity, effectiveness
            timestamp = entry["timestamp"].strftime("%H:%M:%S")
            activity = entry["activity"]
            effectiveness = entry.get("effectiveness")

            # Row Frame
            row_frame = ctk.CTkFrame(self.scroll_frame)
            row_frame.pack(pady=2, padx=5, fill="x")

            # Time label
            lbl_time = ctk.CTkLabel(
                row_frame, text=timestamp, text_color="gray", width=70, font=("Arial", 11)
            )
            lbl_time.pack(side="left", padx=5)

            # Effectiveness indicator
            if effectiveness:
                eff_text = "Good" if effectiveness == "good" else "Bad"
                eff_color = "#4CAF50" if effectiveness == "good" else "#EF5350"
                lbl_eff = ctk.CTkLabel(
                    row_frame,
                    text=eff_text,
                    text_color=eff_color,
                    width=40,
                    font=("Arial", 10),
                )
                lbl_eff.pack(side="left", padx=2)

            # Activity label
            lbl_comment = ctk.CTkLabel(row_frame, text=activity, anchor="w", wraplength=350)
            lbl_comment.pack(side="left", padx=5, fill="x", expand=True)
