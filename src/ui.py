"""UI components for the Stay-On-Track application."""

import datetime
import os
import subprocess

import customtkinter as ctk


class InputWindow(ctk.CTkToplevel):
    """3-step activity logging window with goal assignment."""

    def __init__(self, storage_manager, goal_manager, gamification_manager, on_close_callback=None):
        super().__init__()
        self.storage_manager = storage_manager
        self.goal_manager = goal_manager
        self.gamification_manager = gamification_manager
        self.on_close_callback = on_close_callback

        # State management
        self.current_step = 1
        self.activity_text = ""
        self.selected_effectiveness = None
        self.selected_goal_id = None
        self.entry_id = None  # Will be set after saving activity

        # UI elements
        self.main_frame = None
        self.title_label = None
        self.content_frame = None
        
        # New state for time selection
        self.selected_time = None

        # Configure window
        self.title("Stay On Track - Log Activity")
        self.geometry("450x500")
        self.attributes("-topmost", True)
        self.resizable(True, True)

        # Initialize UI
        self._create_main_ui()
        self._show_step_1()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _create_main_ui(self):
        """Create the main UI structure."""
        # Navigation buttons frame (Pack FIRST to stick to bottom)
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(side="bottom", fill="x", pady=20)

        # Main container for top content
        top_container = ctk.CTkFrame(self, fg_color="transparent")
        top_container.pack(side="top", fill="both", expand=True)

        # Title
        self.title_label = ctk.CTkLabel(top_container, text="", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=(20, 10))

        # Content frame
        self.content_frame = ctk.CTkFrame(top_container, fg_color="transparent")
        self.content_frame.pack(pady=10, padx=20, fill="both", expand=True)

    def _clear_content_frame(self):
        """Clear all widgets from content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _clear_nav_frame(self):
        """Clear all widgets from navigation frame."""
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

    # =========================================================================
    # Step 1: Activity Input
    # =========================================================================

    def _show_step_1(self):
        """Show step 1: Activity text input and Time selection."""
        self.current_step = 1
        self.title_label.configure(text="📝 What have you been working on?")
        self.selected_time = None

        self._clear_content_frame()
        self._clear_nav_frame()

        # --- Time Input Section ---
        time_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        time_frame.pack(fill="x", pady=(0, 10))

        time_label = ctk.CTkLabel(time_frame, text="Time:", font=("Arial", 12))
        time_label.pack(side="left", padx=(0, 10))

        # Default to "Now" (empty or explicit time)
        self.time_entry = ctk.CTkEntry(
            time_frame,
            width=80,
            height=30,
            placeholder_text="Now",
            font=("Arial", 12),
        )
        self.time_entry.pack(side="left")
        
        ctk.CTkLabel(time_frame, text="(HH:MM)", text_color="gray", font=("Arial", 10)).pack(side="left", padx=5)

        # --- Activity Input ---
        self.activity_entry = ctk.CTkEntry(
            self.content_frame,
            width=350,
            height=40,
            placeholder_text="Describe your activity...",
            font=("Arial", 12),
            border_color=["#979DA2", "#565B5E"]
        )
        self.activity_entry.pack(pady=(5, 15))
        self.activity_entry.focus_set()

        # --- Smart Backfill / Recent Section ---
        
        # 1. Detect missing slots in the last 90 minutes
        missing_slots = self._detect_missing_slots()
        
        if missing_slots:
            backfill_label = ctk.CTkLabel(
                self.content_frame, 
                text="⚠️ Missing logs found (Quick Backfill):", 
                font=("Arial", 11, "bold"),
                text_color="#E65100"
            )
            backfill_label.pack(pady=(0, 5))
            
            for slot_time in missing_slots:
                time_str = slot_time.strftime("%H:%M")
                btn = ctk.CTkButton(
                    self.content_frame,
                    text=f"📍 Log missing slot: {time_str}",
                    font=("Arial", 11, "bold"),
                    fg_color="#FFF8E1", # Light Amber
                    text_color="#BF360C", # Deep Orange
                    border_color="#FFE082",
                    border_width=1,
                    hover_color="#FFECB3",
                    height=36, # Slightly taller for better touch/click
                    anchor="w",
                    command=lambda t=time_str: self._set_backfill_time(t)
                )
                btn.pack(fill="x", pady=4, padx=5) # Better padding
                
            # Aesthetic separator
            sep_container = ctk.CTkFrame(self.content_frame, height=30, fg_color="transparent")
            sep_container.pack(fill="x", pady=(15, 5))
            ctk.CTkLabel(sep_container, text="OR RESUME RECENT DESCRIPTION", font=("Arial", 9, "bold"), text_color="gray").pack(pady=5)
            # Subtle line
            ctk.CTkFrame(self.content_frame, height=1, fg_color=["#E0E0E0", "#333333"]).pack(fill="x", padx=20, pady=(0, 10))

        # 2. Recent activities (Filtered for TODAY only)
        recent_entries = self.storage_manager.get_recent_entries(limit=10) # Get more to filter
        todays_entries = []
        seen_activities = set()
        
        today = datetime.date.today()
        if recent_entries:
            for entry in recent_entries:
                # Filter: Must be today AND unique
                if entry["timestamp"].date() == today:
                    act = entry["activity"]
                    if act not in seen_activities:
                        todays_entries.append(entry)
                        seen_activities.add(act)
                        if len(todays_entries) >= 3: break

        if todays_entries:
            recent_label = ctk.CTkLabel(
                self.content_frame, text="Quick reuse from today:", font=("Arial", 11, "bold")
            )
            recent_label.pack(pady=(0, 8))

            for entry in todays_entries:
                timestamp = entry["timestamp"].strftime("%H:%M")
                activity = entry["activity"]
                display_text = (
                    f"{timestamp} - {activity[:35]}..."
                    if len(activity) > 35
                    else f"{timestamp} - {activity}"
                )

                recent_btn = ctk.CTkButton(
                    self.content_frame,
                    text=display_text,
                    font=("Arial", 10),
                    fg_color="#F5F5F5",
                    text_color="#333333",
                    hover_color="#E0E0E0",
                    height=32,
                    anchor="w",
                    command=lambda a=activity: self._use_recent_activity(a),
                )
                recent_btn.pack(fill="x", pady=2)

        # Navigation
        self._create_step_navigation("Next →", self._next_from_step_1)

    def _detect_missing_slots(self):
        """Check for empty 15-min slots in the last 90 minutes."""
        now = datetime.datetime.now()
        # Round down to nearest 15 min
        minutes = (now.minute // 15) * 15
        current_slot = now.replace(minute=minutes, second=0, microsecond=0)
        
        missing_slots = []
        # Check last 6 slots (90 mins), skipping current one
        for i in range(1, 7): 
            check_time = current_slot - datetime.timedelta(minutes=15 * i)
            end_time = check_time + datetime.timedelta(minutes=15)
            
            # Query storage for entries in this range
            count = self.storage_manager.get_entries_count_for_range(check_time, end_time)
            
            if count == 0:
                missing_slots.append(check_time)
                if len(missing_slots) >= 3: # Limit to 3 suggestions
                    break
                    
        return missing_slots

    def _set_backfill_time(self, time_str):
        """Set the time input field and focus activity entry."""
        self.time_entry.delete(0, "end")
        self.time_entry.insert(0, time_str)
        # Visual feedback
        self.time_entry.configure(border_color="#4CAF50") # Green border
        self.activity_entry.focus_set() # Focus activity entry for immediate typing
        self.after(500, lambda: self.time_entry.configure(border_color=["#979DA2", "#565B5E"]))

    def _use_recent_activity(self, activity):
        """Use a recent activity as input."""
        self.activity_entry.delete(0, "end")
        self.activity_entry.insert(0, activity)

    def _next_from_step_1(self):
        """Handle next button from step 1."""
        self.activity_text = self.activity_entry.get().strip()
        time_text = self.time_entry.get().strip()
        
        # Validate Time
        if time_text and time_text.lower() != "now":
            try:
                # Try parsing HH:MM
                valid_time = datetime.datetime.strptime(time_text, "%H:%M").time()
                # Combine with today's date
                self.selected_time = datetime.datetime.combine(datetime.date.today(), valid_time)
            except ValueError:
                self.time_entry.configure(border_color="red")
                return
        else:
            self.selected_time = None # Means "Now"

        if not self.activity_text:
            # Show error briefly
            self.activity_entry.configure(border_color="red")
            self.after(
                1000, lambda: self.activity_entry.configure(border_color=["#979DA2", "#565B5E"])
            )
            return

        self._show_step_2()

    # =========================================================================
    # Step 2: Effectiveness Rating
    # =========================================================================

    def _show_step_2(self):
        """Show step 2: Effectiveness rating."""
        self.current_step = 2
        self.title_label.configure(text=f"📝 '{self.activity_text[:30]}...'")

        self._clear_content_frame()
        self._clear_nav_frame()

        # Question
        question_label = ctk.CTkLabel(
            self.content_frame, text="How effective was this activity?", font=("Arial", 14)
        )
        question_label.pack(pady=(20, 15))

        # Effectiveness buttons
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.btn_good = ctk.CTkButton(
            btn_frame,
            text="😊 Good",
            width=120,
            height=45,
            font=("Arial", 12, "bold"),
            fg_color="#E8F5E9",
            text_color="#2E7D32",
            hover_color="#C8E6C9",
            command=lambda: self._select_effectiveness("good"),
        )
        self.btn_good.pack(side="left", padx=15)

        self.btn_bad = ctk.CTkButton(
            btn_frame,
            text="😞 Bad",
            width=120,
            height=45,
            font=("Arial", 12, "bold"),
            fg_color="#FFEBEE",
            text_color="#C62828",
            hover_color="#FFCDD2",
            command=lambda: self._select_effectiveness("bad"),
        )
        self.btn_bad.pack(side="left", padx=15)

        # Skip option
        skip_label = ctk.CTkLabel(
            self.content_frame, text="Or skip this step", font=("Arial", 10), text_color="gray"
        )
        skip_label.pack(pady=(10, 0))

        # Navigation
        self._create_step_navigation("← Back", self._show_step_1, "Next →", self._next_from_step_2)

    def _select_effectiveness(self, value):
        """Handle effectiveness button selection."""
        self.selected_effectiveness = value

        # Update button colors
        if value == "good":
            self.btn_good.configure(fg_color="#4CAF50", text_color="white")
            self.btn_bad.configure(fg_color="#FFEBEE", text_color="#C62828")
        else:
            self.btn_good.configure(fg_color="#E8F5E9", text_color="#2E7D32")
            self.btn_bad.configure(fg_color="#EF5350", text_color="white")

    def _next_from_step_2(self):
        """Handle next button from step 2."""
        self._show_step_3()

    # =========================================================================
    # Step 3: Goal Assignment
    # =========================================================================

    def _show_step_3(self):
        """Show step 3: Goal assignment."""
        self.current_step = 3
        self.title_label.configure(text=f"🎯 '{self.activity_text[:25]}...'")

        self._clear_content_frame()
        self._clear_nav_frame()

        # Question
        question_label = ctk.CTkLabel(
            self.content_frame, text="Which goal did this move forward?", font=("Arial", 14)
        )
        question_label.pack(pady=(20, 15))

        # Get daily focus goals
        daily_goals = self.goal_manager.get_daily_focus_today()

        # Goal selection
        self.goal_var = ctk.StringVar(value="none")

        if daily_goals:
            # Show daily goals
            for _i, goal in enumerate(daily_goals):
                goal_name = goal["goal_name"] or goal["adhoc_name"]
                radio_btn = ctk.CTkRadioButton(
                    self.content_frame,
                    text=goal_name,
                    variable=self.goal_var,
                    value=f"goal_{goal['goal_id'] or 'adhoc_' + str(goal['id'])}",
                    font=("Arial", 11),
                )
                radio_btn.pack(anchor="w", pady=3, padx=20)
        else:
            # No daily goals set
            no_goals_label = ctk.CTkLabel(
                self.content_frame,
                text="No daily goals set yet.\nSet them in the morning for better tracking!",
                font=("Arial", 11),
                text_color="gray",
            )
            no_goals_label.pack(pady=10)

        # "Manage Daily Focus" Button
        manage_daily_btn = ctk.CTkButton(
            self.content_frame,
            text=" ⚙️ Edit Today's Focus Goals ",
            font=("Arial", 11),
            fg_color="transparent",
            border_color="#979DA2",
            border_width=1,
            text_color=["#333333", "#CCCCCC"],
            hover_color=["#F0F0F0", "#3D3D3D"],
            height=28,
            command=self._open_daily_focus
        )
        manage_daily_btn.pack(pady=(10, 15))

        # None option
        none_radio = ctk.CTkRadioButton(
            self.content_frame,
            text="None / Unrelated activity",
            variable=self.goal_var,
            value="none",
            font=("Arial", 11),
        )
        none_radio.pack(anchor="w", pady=(10, 5), padx=20)

        # Navigation
        self._create_step_navigation("← Back", self._show_step_2, "Save ✓", self._save_entry)

    def _save_entry(self):
        """Save the complete entry and close."""
        # Parse goal selection
        goal_value = self.goal_var.get()
        if goal_value.startswith("goal_"):
            goal_part = goal_value[5:]  # Remove "goal_" prefix
            if goal_part.startswith("adhoc_"):
                # For adhoc goals, we don't link to goal_id (they're not in goals table)
                self.selected_goal_id = None
            else:
                try:
                    self.selected_goal_id = int(goal_part)
                except ValueError:
                    self.selected_goal_id = None
        else:
            self.selected_goal_id = None

        # Save entry
        self.entry_id = self.storage_manager.save_entry(
            self.activity_text, 
            self.selected_effectiveness,
            custom_timestamp=self.selected_time
        )

        # Link to goal if selected
        if self.selected_goal_id is not None:
            self.goal_manager.link_activity_to_goal(self.entry_id, self.selected_goal_id)

        # Update streak and check achievements
        self.gamification_manager.update_streak()
        self.gamification_manager.check_and_unlock_achievements()

        # Close window
        self.on_close()

    def _open_daily_focus(self):
        """Open the daily focus window to manage goals."""
        from goals.daily_focus_ui import DailyFocusWindow
        
        # Hide current window temporarily or just keep it open? 
        # Better to keep open but maybe minimize interference.
        
        # We need a callback that reloads Step 3 when the focus window closes
        def on_focus_closed():
            if self.winfo_exists():
                self.focus_force()
                self._show_step_3() # Reload step 3 to see new goals

        focus_window = DailyFocusWindow(
            self.goal_manager, 
            self.gamification_manager, 
            on_complete_callback=on_focus_closed
        )
        focus_window.lift()
        focus_window.focus_force()

    # =========================================================================
    # Navigation Helpers
    # =========================================================================

    def _create_step_navigation(
        self, left_text=None, left_command=None, right_text=None, right_command=None
    ):
        """Create navigation buttons for steps."""
        if left_text and left_command:
            left_btn = ctk.CTkButton(
                self.nav_frame,
                text=left_text,
                width=100,
                height=35,
                fg_color="#F5F5F5",
                text_color="#333333",
                hover_color="#E0E0E0",
                command=left_command,
            )
            left_btn.pack(side="left", padx=10)

        if right_text and right_command:
            right_btn = ctk.CTkButton(
                self.nav_frame, text=right_text, width=100, height=35, command=right_command
            )
            right_btn.pack(side="right", padx=10)

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
        start_time = self.ent_start.get().strip()
        end_time = self.ent_end.get().strip()
        
        # Basic validation
        try:
            for t in [start_time, end_time]:
                if len(t.split(':')) != 2: raise ValueError
                h, m = map(int, t.split(':'))
                if not (0 <= h <= 23 and 0 <= m <= 59): raise ValueError
        except (ValueError, AttributeError):
            self.ent_start.configure(border_color="red")
            self.ent_end.configure(border_color="red")
            return

        new_config = {
            "start_time": start_time,
            "end_time": end_time,
        }
        self.config_manager.save_config(new_config)

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()


class HistoryWindow(ctk.CTkToplevel):
    """Window for viewing activity history with date navigation."""

    def __init__(self, storage_manager, goal_manager=None):
        super().__init__()
        self.storage_manager = storage_manager
        self.goal_manager = goal_manager
        self.current_date = datetime.date.today()
        self.title("Activity Log")
        self.geometry("550x650")
        self.attributes("-topmost", True)

        # Navigation Bar (Central Header)
        self.nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_bar.pack(fill="x", padx=10, pady=(10, 5))
        
        self._create_nav_button(self.nav_bar, "📋 Log", "current").pack(side="left", expand=True, padx=2)
        self._create_nav_button(self.nav_bar, "📊 Analytics", lambda: self._switch_to("analytics")).pack(side="left", expand=True, padx=2)
        self._create_nav_button(self.nav_bar, "🎯 Goals", lambda: self._switch_to("goals")).pack(side="left", expand=True, padx=2)

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
            timestamp = entry["timestamp"].strftime("%H:%M")
            activity = entry["activity"]
            effectiveness = entry.get("effectiveness")

            # Row Frame (Card style)
            row_frame = ctk.CTkFrame(
                self.scroll_frame, 
                fg_color=["#FAFAFA", "#2D2D2D"],
                border_color=["#EEEEEE", "#3D3D3D"],
                border_width=1
            )
            row_frame.pack(pady=4, padx=8, fill="x")

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
                    font=("Arial", 10, "bold"),
                )
                lbl_eff.pack(side="left", padx=2)

            # Activity text (The missing part)
            activity_display = activity
            
            # Show linked goal if available
            goal_id = entry.get("goal_id")
            if goal_id and self.goal_manager:
                goal_name = self.goal_manager.get_goal_name(goal_id)
                if goal_name:
                    activity_display = f"[{goal_name}] {activity}"

            lbl_activity = ctk.CTkLabel(
                row_frame,
                text=activity_display,
                font=("Arial", 12),
                anchor="w",
                justify="left",
                wraplength=380  # Professional wrapping for readability
            )
            lbl_activity.pack(side="left", padx=(10, 5), fill="x", expand=True)

    def _create_nav_button(self, parent, text, command):
        """Helper to create consistent navigation buttons."""
        is_current = command == "current"
        return ctk.CTkButton(
            parent,
            text=text,
            height=32,
            fg_color="#1976D2" if is_current else "#F5F5F5",
            text_color="white" if is_current else "#333333",
            hover_color="#1565C0" if is_current else "#E0E0E0",
            command=None if is_current else command
        )

    def _switch_to(self, target):
        """Switch to another window via the main app instance."""
        # Find the main app instance
        parent = self.master
        while parent and not hasattr(parent, "open_analytics"):
            if hasattr(parent, "master"):
                parent = parent.master
            else:
                break
        
        if parent:
            if target == "analytics":
                parent.open_analytics()
            elif target == "goals":
                parent.open_goal_management()
            self.destroy()
