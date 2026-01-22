"""First-time goal setup wizard for Stay-On-Track."""

import customtkinter as ctk


class GoalSetupWindow(ctk.CTkToplevel):
    """Wizard for setting up initial goals on first launch."""

    PREDEFINED_GOALS = [
        "Career Growth",
        "Health & Fitness",
        "Learning & Skills",
        "Project Completion",
        "Personal Development",
        "Financial Goals",
        "Relationships",
        "Creative Pursuits",
    ]

    def __init__(self, goal_manager, on_complete_callback=None):
        super().__init__()
        self.goal_manager = goal_manager
        self.on_complete_callback = on_complete_callback

        # State
        self.selected_goals = []
        self.custom_goals = []
        self.current_step = 1

        # Configure window
        self.title("Welcome to Stay-On-Track!")
        self.geometry("500x600")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Initialize UI
        self._create_main_ui()
        self._show_step_1()

        self.protocol("WM_DELETE_WINDOW", self._on_skip)

    def _create_main_ui(self):
        """Create the main UI structure."""
        # Title
        self.title_label = ctk.CTkLabel(self, text="", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=(30, 10))

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="gray")
        self.subtitle_label.pack(pady=(0, 20))

        # Content frame
        self.content_frame = ctk.CTkScrollableFrame(self, width=450, height=350)
        self.content_frame.pack(pady=10, padx=25, fill="both", expand=True)

        # Navigation frame
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(pady=(20, 30))

    def _clear_content_frame(self):
        """Clear all widgets from content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _clear_nav_frame(self):
        """Clear all widgets from navigation frame."""
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

    def _show_step_1(self):
        """Show step 1: Welcome and goal category selection."""
        self.current_step = 1
        self.title_label.configure(text="🎯 Welcome to Stay-On-Track!")
        self.subtitle_label.configure(text="Let's set up some goals to help you stay focused.")

        self._clear_content_frame()
        self._clear_nav_frame()

        # Introduction text
        intro_label = ctk.CTkLabel(
            self.content_frame,
            text="What areas of your life would you like to focus on?\n\nSelect up to 3 areas that matter most to you:",
            font=("Arial", 12),
            wraplength=400,
            justify="center",
        )
        intro_label.pack(pady=(10, 20))

        # Goal selection checkboxes
        self.goal_vars = {}
        for goal in self.PREDEFINED_GOALS:
            var = ctk.BooleanVar(value=False)
            self.goal_vars[goal] = var

            checkbox = ctk.CTkCheckBox(
                self.content_frame,
                text=goal,
                variable=var,
                font=("Arial", 11),
                command=self._update_goal_selection,
            )
            checkbox.pack(anchor="w", pady=3, padx=20)

        # Custom goal input
        custom_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        custom_frame.pack(pady=(20, 10), fill="x")

        custom_label = ctk.CTkLabel(
            custom_frame, text="Or add your own:", font=("Arial", 11, "bold")
        )
        custom_label.pack(anchor="w", pady=(0, 5))

        self.custom_entry = ctk.CTkEntry(
            custom_frame, placeholder_text="e.g., Learn Spanish, Start a blog...", width=300
        )
        self.custom_entry.pack(pady=(0, 5))

        self.add_custom_btn = ctk.CTkButton(
            custom_frame, text="+ Add", width=80, height=30, command=self._add_custom_goal
        )
        self.add_custom_btn.pack(pady=(0, 10))

        # Selected goals display
        self.selection_label = ctk.CTkLabel(
            self.content_frame, text="Selected: 0/3", font=("Arial", 10), text_color="gray"
        )
        self.selection_label.pack(pady=(10, 0))

        # Navigation
        self._create_step_navigation(
            "Skip for now", self._on_skip, "Continue →", self._next_from_step_1
        )

    def _update_goal_selection(self):
        """Update the goal selection counter."""
        selected_count = sum(1 for var in self.goal_vars.values() if var.get())
        total_selected = selected_count + len(self.custom_goals)

        self.selection_label.configure(text=f"Selected: {total_selected}/3")

        # Disable checkboxes if limit reached
        for goal, var in self.goal_vars.items():
            checkbox = None
            for child in self.content_frame.winfo_children():
                if isinstance(child, ctk.CTkCheckBox) and child.cget("text") == goal:
                    checkbox = child
                    break

            if checkbox:
                if total_selected >= 3 and not var.get():
                    checkbox.configure(state="disabled")
                else:
                    checkbox.configure(state="normal")

    def _add_custom_goal(self):
        """Add a custom goal to the selection."""
        custom_text = self.custom_entry.get().strip()
        if not custom_text:
            return

        if len(self.custom_goals) + sum(1 for var in self.goal_vars.values() if var.get()) >= 3:
            return  # Limit reached

        if custom_text not in self.custom_goals:
            self.custom_goals.append(custom_text)
            self.custom_entry.delete(0, "end")
            self._update_goal_selection()

            # Add to display
            self._refresh_custom_goals_display()

    def _refresh_custom_goals_display(self):
        """Refresh the display of custom goals."""
        # Find and remove existing custom goals display
        for child in self.content_frame.winfo_children():
            if hasattr(child, "custom_goals_frame"):
                child.destroy()

        if self.custom_goals:
            custom_display_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            custom_display_frame.custom_goals_frame = True
            custom_display_frame.pack(pady=(10, 0), fill="x")

            for goal in self.custom_goals:
                goal_frame = ctk.CTkFrame(custom_display_frame, fg_color="transparent")
                goal_frame.pack(fill="x", pady=2)

                goal_label = ctk.CTkLabel(
                    goal_frame, text=f"✓ {goal}", font=("Arial", 11), anchor="w"
                )
                goal_label.pack(side="left", padx=(20, 0))

                remove_btn = ctk.CTkButton(
                    goal_frame,
                    text="✕",
                    width=30,
                    height=20,
                    font=("Arial", 10),
                    fg_color="#FFEBEE",
                    text_color="#C62828",
                    command=lambda g=goal: self._remove_custom_goal(g),
                )
                remove_btn.pack(side="right", padx=(0, 20))

    def _remove_custom_goal(self, goal):
        """Remove a custom goal from selection."""
        if goal in self.custom_goals:
            self.custom_goals.remove(goal)
            self._update_goal_selection()
            self._refresh_custom_goals_display()

    def _next_from_step_1(self):
        """Handle continue button from step 1."""
        # Collect selected goals
        self.selected_goals = []
        for goal, var in self.goal_vars.items():
            if var.get():
                self.selected_goals.append(goal)

        self.selected_goals.extend(self.custom_goals)

        if not self.selected_goals:
            # Show message to select at least one goal
            self._show_no_goals_message()
            return

        self._show_step_2()

    def _show_no_goals_message(self):
        """Show message when no goals are selected."""
        # Create overlay message
        overlay = ctk.CTkFrame(self, fg_color="#FFF3CD", corner_radius=8)
        overlay.place(relx=0.5, rely=0.5, anchor="center")

        message_label = ctk.CTkLabel(
            overlay,
            text="Please select at least one goal\nto continue with the setup.",
            font=("Arial", 12),
            text_color="#856404",
        )
        message_label.pack(pady=20, padx=20)

        ok_btn = ctk.CTkButton(overlay, text="OK", command=overlay.destroy)
        ok_btn.pack(pady=(0, 20))

    def _show_step_2(self):
        """Show step 2: Confirmation and completion."""
        self.current_step = 2
        self.title_label.configure(text="🎉 You're all set!")
        self.subtitle_label.configure(text="Your goals have been saved. Let's start tracking!")

        self._clear_content_frame()
        self._clear_nav_frame()

        # Summary
        summary_label = ctk.CTkLabel(
            self.content_frame, text="Your selected goals:", font=("Arial", 14, "bold")
        )
        summary_label.pack(pady=(20, 15))

        # List selected goals
        for goal in self.selected_goals:
            goal_label = ctk.CTkLabel(
                self.content_frame, text=f"✓ {goal}", font=("Arial", 12), anchor="w"
            )
            goal_label.pack(fill="x", pady=3, padx=40)

        # Explanation
        explanation_label = ctk.CTkLabel(
            self.content_frame,
            text="\n💡 Tip: Set your daily focus each morning for the best results.\nYou can always change your goals later in the settings.",
            font=("Arial", 11),
            text_color="gray",
            wraplength=400,
            justify="center",
        )
        explanation_label.pack(pady=(30, 20))

        # Navigation
        self._create_step_navigation(
            None, None, "Start Using Stay-On-Track! →", self._complete_setup
        )

    def _complete_setup(self):
        """Complete the setup and save goals."""
        # Save goals to database
        for goal_name in self.selected_goals:
            self.goal_manager.create_goal(goal_name)

        # Call completion callback
        if self.on_complete_callback:
            self.on_complete_callback()

        # Close window
        self.destroy()

    def _on_skip(self):
        """Handle skip button - close without saving."""
        if self.on_complete_callback:
            self.on_complete_callback()
        self.destroy()

    def _create_step_navigation(
        self, left_text=None, left_command=None, right_text=None, right_command=None
    ):
        """Create navigation buttons for steps."""
        if left_text and left_command:
            left_btn = ctk.CTkButton(
                self.nav_frame,
                text=left_text,
                width=120,
                height=35,
                fg_color="#F5F5F5",
                text_color="#333333",
                hover_color="#E0E0E0",
                command=left_command,
            )
            left_btn.pack(side="left", padx=10)

        if right_text and right_command:
            right_btn = ctk.CTkButton(
                self.nav_frame, text=right_text, width=200, height=35, command=right_command
            )
            right_btn.pack(side="right", padx=10)
