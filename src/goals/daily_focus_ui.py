"""Daily focus selection window for Stay-On-Track."""

import customtkinter as ctk
from goals.goal_bulk_manage_ui import GoalBulkManageWindow


class DailyFocusWindow(ctk.CTkToplevel):
    """Window for selecting daily focus goals."""

    def __init__(self, goal_manager, gamification_manager, on_complete_callback=None):
        super().__init__()
        self.goal_manager = goal_manager
        self.gamification_manager = gamification_manager
        self.on_complete_callback = on_complete_callback

        # State
        self.selected_goals = []
        self.adhoc_goal_text = ""

        # Configure window
        self.title("Daily Focus - Stay On Track")
        self.geometry("450x600")  # Slightly taller
        self.attributes("-topmost", True)
        self.resizable(True, True)  # Allow resizing

        # Initialize UI
        self._create_main_ui()
        self._load_content()

        self.protocol("WM_DELETE_WINDOW", self._on_skip)

    def _create_main_ui(self):
        """Create the main UI structure."""
        # Navigation frame (Pack FIRST to stick to bottom)
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(side="bottom", fill="x", pady=20, padx=20)

        # Main container for top content
        top_container = ctk.CTkFrame(self, fg_color="transparent")
        top_container.pack(side="top", fill="both", expand=True)

        # Title
        self.title_label = ctk.CTkLabel(top_container, text="☀️ Good morning!", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=(25, 5))

        # Motivational quote
        self.quote_label = ctk.CTkLabel(
            top_container,
            text=self.gamification_manager.get_morning_quote(),
            font=("Arial", 11),
            text_color="#4CAF50",
            wraplength=400,
        )
        self.quote_label.pack(pady=(0, 20))

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            top_container, text="What are your 3 priorities today?", font=("Arial", 14)
        )
        self.subtitle_label.pack(pady=(0, 15))

        # Streak display (Pack BEFORE content frame to sit above it, or AFTER to sit below?)
        # Original was below content. Let's put it below content but above nav.
        self.streak_frame = ctk.CTkFrame(top_container, fg_color="transparent")
        self.streak_frame.pack(side="bottom", pady=(10, 0))

        # Content frame
        self.content_frame = ctk.CTkScrollableFrame(top_container, width=400)
        self.content_frame.pack(pady=5, padx=25, fill="both", expand=True)


    def _load_content(self):
        """Load and display available goals and suggestions."""
        self._clear_content_frame()

        # Get available goals
        available_goals = self.goal_manager.get_active_goals()

        # Get recent adhoc goals as suggestions
        recent_adhoc = self.goal_manager.get_daily_focus_suggestions()

        # Current streak
        streak_info = self.gamification_manager.get_streak_info()
        if streak_info["current"] > 0:
            streak_text = f"🔥 {streak_info['current']}-day streak! Keep it going!"
            if streak_info["next_milestone"]:
                progress_pct = int(streak_info["progress_to_next"] * 100)
                streak_text += f" ({progress_pct}% to {streak_info['next_milestone']} days)"

            streak_label = ctk.CTkLabel(
                self.streak_frame,
                text=streak_text,
                font=("Arial", 11, "bold"),
                text_color="#FF6B35",
            )
            streak_label.pack(pady=5)

        # Instructions
        if available_goals:
            instructions = ctk.CTkLabel(
                self.content_frame,
                text="Select up to 3 goals for today:",
                font=("Arial", 12, "bold"),
            )
            instructions.pack(pady=(10, 15))
        else:
            # No goals available
            no_goals_label = ctk.CTkLabel(
                self.content_frame,
                text="No goals set up yet.\n\nFirst, set up your main goals in the goal setup wizard.\nThen come back here to select your daily focus.",
                font=("Arial", 12),
                wraplength=350,
                justify="center",
            )
            no_goals_label.pack(pady=50)

            # Show setup button
            setup_btn = ctk.CTkButton(
                self.content_frame, text="Set Up Goals Now", command=self._open_goal_setup
            )
            setup_btn.pack(pady=20)
            return

        # Goal selection checkboxes
        self.goal_vars = {}
        self.checkboxes = {} # Direct references
        for goal in available_goals:
            var = ctk.BooleanVar(value=False)
            self.goal_vars[goal["id"]] = var

            # Show subgoals indented
            display_name = goal["name"]
            if goal["parent_id"]:
                display_name = f"  └─ {display_name}"

            checkbox = ctk.CTkCheckBox(
                self.content_frame,
                text=display_name,
                variable=var,
                font=("Arial", 11),
                command=self._update_selection_count,
            )
            checkbox.pack(anchor="w", pady=2, padx=20)
            self.checkboxes[goal["id"]] = checkbox

        # Adhoc goal suggestions
        if recent_adhoc:
            suggestions_label = ctk.CTkLabel(
                self.content_frame, text="Recent tasks (click to add):", font=("Arial", 11, "bold")
            )
            suggestions_label.pack(pady=(20, 10), anchor="w", padx=20)

            for adhoc_goal in recent_adhoc[:3]:  # Show max 3 suggestions
                suggestion_btn = ctk.CTkButton(
                    self.content_frame,
                    text=f"+ {adhoc_goal}",
                    font=("Arial", 10),
                    fg_color="#E8F5E9",
                    text_color="#2E7D32",
                    hover_color="#C8E6C9",
                    height=28,
                    command=lambda g=adhoc_goal: self._add_adhoc_goal(g),
                )
                suggestion_btn.pack(anchor="w", pady=1, padx=40)

        # Custom adhoc goal input
        custom_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        custom_frame.pack(pady=(20, 10), fill="x")

        custom_label = ctk.CTkLabel(
            custom_frame, text="Add a specific task for today:", font=("Arial", 11, "bold")
        )
        custom_label.pack(anchor="w", pady=(0, 5))

        self.adhoc_entry = ctk.CTkEntry(
            custom_frame, placeholder_text="e.g., Finish client report, Call mom...", width=300
        )
        self.adhoc_entry.pack(pady=(0, 5))

        self.add_adhoc_btn = ctk.CTkButton(
            custom_frame, text="+ Add", width=80, height=30, command=self._add_custom_adhoc_goal
        )
        self.add_adhoc_btn.pack(pady=(0, 10))

        # Selection counter
        self.selection_label = ctk.CTkLabel(
            self.content_frame, text="Selected: 0/3", font=("Arial", 10), text_color="gray"
        )
        self.selection_label.pack(pady=(10, 0))

        # Navigation
        self._create_navigation()

    def _clear_content_frame(self):
        """Clear all widgets from content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _update_selection_count(self):
        """Update the selection counter."""
        selected_count = sum(1 for var in self.goal_vars.values() if var.get())
        selected_count += len(self.selected_goals) if hasattr(self, "selected_goals") else 0

        self.selection_label.configure(text=f"Selected: {selected_count}/3")

        self.selection_label.configure(text=f"Selected: {selected_count}/3")

        # Disable checkboxes if limit reached
        for goal_id, var in self.goal_vars.items():
            checkbox = self.checkboxes.get(goal_id)
            if checkbox:
                if selected_count >= 3 and not var.get():
                    checkbox.configure(state="disabled")
                else:
                    checkbox.configure(state="normal")

    def _add_adhoc_goal(self, goal_text):
        """Add a suggested adhoc goal."""
        if len(self.selected_goals) >= 3:
            return

        if goal_text not in [g.get("adhoc_name", "") for g in self.selected_goals]:
            self.selected_goals.append({"adhoc_name": goal_text})
            self._update_selection_count()
            self._refresh_adhoc_display()

    def _add_custom_adhoc_goal(self):
        """Add a custom adhoc goal."""
        custom_text = self.adhoc_entry.get().strip()
        if not custom_text:
            return

        if len(self.selected_goals) >= 3:
            return

        # Check for duplicates
        if custom_text not in [g.get("adhoc_name", "") for g in self.selected_goals]:
            self.selected_goals.append({"adhoc_name": custom_text})
            self.adhoc_entry.delete(0, "end")
            self._update_selection_count()
            self._refresh_adhoc_display()

    def _refresh_adhoc_display(self):
        """Refresh the display of selected adhoc goals."""
        # Find and remove existing adhoc display
        for child in self.content_frame.winfo_children():
            if hasattr(child, "adhoc_display"):
                child.destroy()

        if self.selected_goals:
            adhoc_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            adhoc_frame.adhoc_display = True
            adhoc_frame.pack(pady=(10, 0), fill="x")

            adhoc_label = ctk.CTkLabel(
                adhoc_frame, text="Today's specific tasks:", font=("Arial", 11, "bold")
            )
            adhoc_label.pack(anchor="w", pady=(0, 5), padx=20)

            for goal in self.selected_goals:
                if "adhoc_name" in goal:
                    goal_frame = ctk.CTkFrame(adhoc_frame, fg_color="transparent")
                    goal_frame.pack(fill="x", pady=2)

                    goal_label = ctk.CTkLabel(
                        goal_frame, text=f"✓ {goal['adhoc_name']}", font=("Arial", 11), anchor="w"
                    )
                    goal_label.pack(side="left", padx=(40, 0))

                    remove_btn = ctk.CTkButton(
                        goal_frame,
                        text="✕",
                        width=30,
                        height=20,
                        font=("Arial", 10),
                        fg_color="#FFEBEE",
                        text_color="#C62828",
                        command=lambda g=goal: self._remove_adhoc_goal(g),
                    )
                    remove_btn.pack(side="right", padx=(0, 20))

    def _remove_adhoc_goal(self, goal):
        """Remove an adhoc goal from selection."""
        if goal in self.selected_goals:
            self.selected_goals.remove(goal)
            self._update_selection_count()
            self._refresh_adhoc_display()

    def _create_navigation(self):
        """Create navigation buttons."""
        self._clear_nav_frame()

        # Manage Goals button
        manage_btn = ctk.CTkButton(
            self.nav_frame,
            text="⚙️ Manage Goals",
            width=120,
            height=35,
            fg_color="#F5F5F5",
            text_color="#333333",
            hover_color="#E0E0E0",
            command=self._open_goal_management,
        )
        manage_btn.pack(side="left", padx=10)

        # Skip button
        skip_btn = ctk.CTkButton(
            self.nav_frame,
            text="Skip Today",
            width=100,
            height=35,
            fg_color="#F5F5F5",
            text_color="#333333",
            hover_color="#E0E0E0",
            command=self._on_skip,
        )
        skip_btn.pack(side="left", padx=10)

        # Start Day button
        start_btn = ctk.CTkButton(
            self.nav_frame,
            text=" Start My Day → ",
            width=160,
            height=40,
            font=("Arial", 13, "bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            command=self._save_and_continue,
        )
        start_btn.pack(side="right", padx=10)

    def _clear_nav_frame(self):
        """Clear all widgets from navigation frame."""
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

    def _save_and_continue(self):
        """Save the daily focus and close."""
        # Collect selected goals
        selected_goal_ids = []
        selected_adhoc = []

        # Regular goals
        for goal_id, var in self.goal_vars.items():
            if var.get():
                selected_goal_ids.append(goal_id)

        # Adhoc goals
        for goal in self.selected_goals:
            if "adhoc_name" in goal:
                selected_adhoc.append(goal["adhoc_name"])

        # Combine into daily focus format
        daily_goals = []
        for goal_id in selected_goal_ids:
            daily_goals.append({"goal_id": goal_id})
        for adhoc_name in selected_adhoc:
            daily_goals.append({"adhoc_name": adhoc_name})

        # Save to database
        self.goal_manager.set_daily_focus(daily_goals)

        # Call completion callback
        if self.on_complete_callback:
            self.on_complete_callback()

        # Close window
        self.destroy()

    def _on_skip(self):
        """Handle skip button."""
        if self.on_complete_callback:
            self.on_complete_callback()
        self.destroy()

    def _open_goal_setup(self):
        """Open goal setup wizard."""
        # This would need to be implemented - for now just close
        self.destroy()

    def _open_goal_management(self):
        """Open improved goal management window."""
        GoalBulkManageWindow(self.goal_manager, on_update_callback=self._load_content)
