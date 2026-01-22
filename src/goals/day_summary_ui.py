"""End-of-day summary window for Stay-On-Track."""

import customtkinter as ctk


class DaySummaryWindow(ctk.CTkToplevel):
    """Window showing end-of-day progress summary."""

    def __init__(self, goal_manager, gamification_manager, storage_manager, on_close_callback=None):
        super().__init__()
        self.goal_manager = goal_manager
        self.gamification_manager = gamification_manager
        self.storage_manager = storage_manager
        self.on_close_callback = on_close_callback

        # Configure window
        self.title("Day Complete - Stay On Track")
        self.geometry("500x650")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Initialize UI
        self._create_main_ui()
        self._load_summary()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_main_ui(self):
        """Create the main UI structure."""
        # Title
        self.title_label = ctk.CTkLabel(self, text="🌙 Day Complete!", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=(25, 5))

        # Motivational quote
        self.quote_label = ctk.CTkLabel(
            self,
            text=self.gamification_manager.get_evening_quote(),
            font=("Arial", 11),
            text_color="#4CAF50",
            wraplength=450,
        )
        self.quote_label.pack(pady=(0, 20))

        # Content frame
        self.content_frame = ctk.CTkScrollableFrame(self, width=450, height=450)
        self.content_frame.pack(pady=5, padx=25, fill="both", expand=True)

        # Navigation frame
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(pady=(15, 25))

    def _load_summary(self):
        """Load and display the day's summary."""
        # Get daily focus goals
        daily_goals = self.goal_manager.get_daily_focus_today()

        # Get goal progress data
        goal_progress = self.goal_manager.get_all_goals_progress(days=1)  # Today only

        # Get today's activities
        today_activities = self.storage_manager.get_today_entries()

        # Calculate effectiveness
        total_activities = len(today_activities)
        effective_activities = sum(1 for a in today_activities if a.get("effectiveness") == "good")
        effectiveness_pct = (
            round(effective_activities / total_activities * 100, 1) if total_activities > 0 else 0
        )

        # Clear content frame
        self._clear_content_frame()

        # Progress section
        if daily_goals:
            progress_label = ctk.CTkLabel(
                self.content_frame,
                text="Today's Progress (based on 15 min per activity):",
                font=("Arial", 14, "bold"),
            )
            progress_label.pack(pady=(20, 15))

            # Show progress for each daily goal
            for goal in daily_goals:
                goal_name = goal["goal_name"] or goal["adhoc_name"]
                goal_id = goal["goal_id"]

                # Find progress data for this goal
                progress_data = None
                if goal_id:
                    for progress in goal_progress:
                        if progress["goal_id"] == goal_id:
                            progress_data = progress
                            break

                # Calculate progress (simplified: activities linked to this goal)
                if progress_data:
                    activities = progress_data["activities"]
                    time_minutes = progress_data["time_minutes"]
                    time_display = self.goal_manager.format_duration(time_minutes)

                    # Create progress bar visualization
                    progress_pct = min(100, time_minutes)  # Simplified: assume 1 hour = 100%
                    bar_length = min(30, int(progress_pct / 3.33))  # Max 30 chars
                    progress_bar = "▓" * bar_length + "░" * (30 - bar_length)

                    # Progress frame
                    progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
                    progress_frame.pack(pady=5, padx=20, fill="x")

                    # Goal name
                    goal_label = ctk.CTkLabel(
                        progress_frame, text=goal_name, font=("Arial", 12, "bold"), anchor="w"
                    )
                    goal_label.pack(fill="x", pady=(0, 3))

                    # Progress bar and stats
                    stats_text = f"{progress_bar}  {time_display}  ({activities} activities)"
                    stats_label = ctk.CTkLabel(
                        progress_frame,
                        text=stats_text,
                        font=("Courier New", 10),
                        text_color="#4CAF50" if progress_pct > 50 else "#FF9800",
                        anchor="w",
                    )
                    stats_label.pack(fill="x")
                else:
                    # No progress for this goal
                    no_progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
                    no_progress_frame.pack(pady=5, padx=20, fill="x")

                    goal_label = ctk.CTkLabel(
                        no_progress_frame,
                        text=f"{goal_name}",
                        font=("Arial", 12, "bold"),
                        anchor="w",
                    )
                    goal_label.pack(fill="x", pady=(0, 3))

                    no_progress_label = ctk.CTkLabel(
                        no_progress_frame,
                        text="░░░░░░░░░░░░░░░░░░░░░░░░░░  0h 0m  (0 activities)",
                        font=("Courier New", 10),
                        text_color="#757575",
                        anchor="w",
                    )
                    no_progress_label.pack(fill="x")
        else:
            # No daily goals set
            no_goals_label = ctk.CTkLabel(
                self.content_frame,
                text="No daily goals were set today.\n\nConsider setting goals tomorrow morning\nto track your progress more effectively.",
                font=("Arial", 12),
                text_color="gray",
                wraplength=400,
                justify="center",
            )
            no_goals_label.pack(pady=50)

        # Effectiveness summary
        if total_activities > 0:
            effectiveness_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            effectiveness_frame.pack(pady=(30, 10), fill="x")

            effectiveness_label = ctk.CTkLabel(
                effectiveness_frame,
                text=f"Effectiveness: {effectiveness_pct}% Good 😊",
                font=("Arial", 14, "bold"),
                text_color="#4CAF50" if effectiveness_pct >= 70 else "#FF9800",
            )
            effectiveness_label.pack(pady=10)

        # Unassigned activities
        unassigned_count = sum(1 for a in today_activities if not a.get("goal_id"))
        if unassigned_count > 0:
            unassigned_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Unassigned Activities: {unassigned_count} ({round(unassigned_count / total_activities * 100, 1) if total_activities > 0 else 0}%)",
                font=("Arial", 11),
                text_color="gray",
            )
            unassigned_label.pack(pady=(5, 0))

        # Streak and achievements
        self._show_gamification_summary()

        # Navigation
        self._create_navigation()

    def _clear_content_frame(self):
        """Clear all widgets from content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_gamification_summary(self):
        """Show streak and achievement summary."""
        gamification_stats = self.gamification_manager.get_gamification_stats()

        # Streak
        streak_info = gamification_stats["streak"]
        if streak_info["current"] > 0:
            streak_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            streak_frame.pack(pady=(20, 5), fill="x")

            streak_text = f"🔥 {streak_info['current']}-day streak!"
            if streak_info["next_milestone"]:
                progress_pct = int(streak_info["progress_to_next"] * 100)
                streak_text += f" ({progress_pct}% to {streak_info['next_milestone']} days)"

            streak_label = ctk.CTkLabel(
                streak_frame, text=streak_text, font=("Arial", 12, "bold"), text_color="#FF6B35"
            )
            streak_label.pack(pady=5)

            if streak_info["longest"] > streak_info["current"]:
                longest_label = ctk.CTkLabel(
                    streak_frame,
                    text=f"Personal best: {streak_info['longest']} days",
                    font=("Arial", 10),
                    text_color="gray",
                )
                longest_label.pack()

        # New achievements
        pending_achievements = self.gamification_manager.get_pending_notifications()
        if pending_achievements:
            achievements_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            achievements_frame.pack(pady=(15, 5), fill="x")

            achievements_title = ctk.CTkLabel(
                achievements_frame,
                text="🏆 New Achievement Unlocked!",
                font=("Arial", 12, "bold"),
                text_color="#FFD700",
            )
            achievements_title.pack(pady=(0, 10))

            for achievement in pending_achievements:
                achievement_label = ctk.CTkLabel(
                    achievements_frame,
                    text=f"{achievement['icon']} {achievement['name']}",
                    font=("Arial", 11, "bold"),
                )
                achievement_label.pack(pady=2)

                desc_label = ctk.CTkLabel(
                    achievements_frame,
                    text=achievement["description"],
                    font=("Arial", 10),
                    text_color="gray",
                    wraplength=400,
                )
                desc_label.pack(pady=(0, 5))

                # Mark as notified
                self.gamification_manager.mark_achievement_notified(achievement["id"])

    def _create_navigation(self):
        """Create navigation buttons."""
        # Clear existing
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

        # Analytics button
        analytics_btn = ctk.CTkButton(
            self.nav_frame,
            text="📊 View Analytics",
            width=140,
            height=35,
            fg_color="#F5F5F5",
            text_color="#333333",
            hover_color="#E0E0E0",
            command=self._open_analytics,
        )
        analytics_btn.pack(side="left", padx=10)

        # Close button
        close_btn = ctk.CTkButton(
            self.nav_frame, text="Close", width=100, height=35, command=self._on_close
        )
        close_btn.pack(side="right", padx=10)

    def _open_analytics(self):
        """Open the analytics window."""
        # This would need to be implemented to open the analytics window
        # For now, just close this window
        self._on_close()

    def _on_close(self):
        """Handle window close."""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
