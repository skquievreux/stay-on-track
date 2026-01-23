"""Goal management interface for Stay-On-Track."""

from tkinter import messagebox

import customtkinter as ctk


class GoalManageWindow(ctk.CTkToplevel):
    """Window for managing goals (add, edit, archive, subgoals)."""

    def __init__(self, goal_manager, on_update_callback=None):
        super().__init__()
        self.goal_manager = goal_manager
        self.on_update_callback = on_update_callback

        # State
        self.editing_goal_id = None
        self.selected_parent_id = None

        # Configure window
        self.title("Manage Goals - Stay On Track")
        self.geometry("550x600")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Initialize UI
        self._create_main_ui()
        self._load_goals()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_main_ui(self):
        """Create the main UI structure."""
        # Title
        title_label = ctk.CTkLabel(self, text="🎯 Manage Goals", font=("Arial", 18, "bold"))
        title_label.pack(pady=(20, 10))

        # Content frame
        self.content_frame = ctk.CTkScrollableFrame(self, width=500, height=400)
        self.content_frame.pack(pady=10, padx=25, fill="both", expand=True)

        # Action buttons frame
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(pady=(10, 20))

        # Add goal button
        add_goal_btn = ctk.CTkButton(
            self.actions_frame, text="+ Add Goal", width=120, height=35, command=self._add_goal
        )
        add_goal_btn.pack(side="left", padx=10)

        # Add subgoal button
        self.add_subgoal_btn = ctk.CTkButton(
            self.actions_frame,
            text="+ Add Sub-goal",
            width=130,
            height=35,
            fg_color="#4CAF50",
            command=self._add_subgoal,
        )
        self.add_subgoal_btn.pack(side="left", padx=10)
        self.add_subgoal_btn.configure(state="disabled")  # Disabled initially

        # Close button
        close_btn = ctk.CTkButton(
            self.actions_frame, text="Close", width=80, height=35, command=self._on_close
        )
        close_btn.pack(side="right", padx=10)

    def _load_goals(self):
        """Load and display all goals."""
        self._clear_content_frame()

        goals_hierarchy = self.goal_manager.get_goal_hierarchy()

        if not goals_hierarchy:
            # No goals yet
            empty_label = ctk.CTkLabel(
                self.content_frame,
                text="No goals created yet.\n\nClick 'Add Goal' to get started!",
                font=("Arial", 12),
                text_color="gray",
                justify="center",
            )
            empty_label.pack(pady=50)
            return

        # Display goals
        for goal in goals_hierarchy:
            self._create_goal_item(goal)

        # Archived goals section
        archived_goals = self._get_archived_goals()
        if archived_goals:
            self._create_archived_section(archived_goals)

    def _create_goal_item(self, goal):
        """Create a display item for a goal."""
        # Main goal frame
        goal_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        goal_frame.pack(fill="x", pady=5, padx=10)

        # Goal content frame
        content_frame = ctk.CTkFrame(goal_frame, fg_color="#F5F5F5", corner_radius=8)
        content_frame.pack(fill="x", padx=5, pady=2)

        # Goal name and actions
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=10)

        goal_label = ctk.CTkLabel(
            header_frame, text=goal["name"], font=("Arial", 13, "bold"), anchor="w"
        )
        goal_label.pack(side="left", fill="x", expand=True)

        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right")

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✎",
            width=30,
            height=25,
            font=("Arial", 10),
            command=lambda: self._edit_goal(goal["id"], goal["name"]),
        )
        edit_btn.pack(side="left", padx=2)

        archive_btn = ctk.CTkButton(
            actions_frame,
            text="🗂️",
            width=30,
            height=25,
            font=("Arial", 10),
            fg_color="#FF9800",
            text_color="white",
            command=lambda: self._archive_goal(goal["id"], goal["name"]),
        )
        archive_btn.pack(side="left", padx=2)

        # Subgoals
        if goal.get("subgoals"):
            for subgoal in goal["subgoals"]:
                self._create_subgoal_item(subgoal, goal["id"])

    def _create_subgoal_item(self, subgoal, parent_id):
        """Create a display item for a subgoal."""
        # Subgoal frame (indented)
        subgoal_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        subgoal_frame.pack(fill="x", pady=2, padx=30)

        # Subgoal content
        sub_content = ctk.CTkFrame(subgoal_frame, fg_color="#E8F5E9", corner_radius=6)
        sub_content.pack(fill="x", padx=5, pady=1)

        # Subgoal header
        sub_header = ctk.CTkFrame(sub_content, fg_color="transparent")
        sub_header.pack(fill="x", padx=12, pady=8)

        sub_label = ctk.CTkLabel(
            sub_header,
            text=f"└─ {subgoal['name']}",
            font=("Arial", 11),
            anchor="w",
            text_color="#2E7D32",
        )
        sub_label.pack(side="left", fill="x", expand=True)

        # Subgoal actions
        sub_actions = ctk.CTkFrame(sub_header, fg_color="transparent")
        sub_actions.pack(side="right")

        sub_edit_btn = ctk.CTkButton(
            sub_actions,
            text="✎",
            width=25,
            height=20,
            font=("Arial", 9),
            command=lambda: self._edit_goal(subgoal["id"], subgoal["name"]),
        )
        sub_edit_btn.pack(side="left", padx=1)

        sub_archive_btn = ctk.CTkButton(
            sub_actions,
            text="🗂️",
            width=25,
            height=20,
            font=("Arial", 9),
            fg_color="#FF9800",
            text_color="white",
            command=lambda: self._archive_goal(subgoal["id"], subgoal["name"]),
        )
        sub_archive_btn.pack(side="left", padx=1)

    def _create_archived_section(self, archived_goals):
        """Create the archived goals section."""
        # Separator
        separator = ctk.CTkFrame(self.content_frame, height=2, fg_color="#DDDDDD")
        separator.pack(fill="x", pady=(20, 10), padx=20)

        # Archived header
        archived_header = ctk.CTkLabel(
            self.content_frame,
            text="📦 Archived Goals",
            font=("Arial", 12, "bold"),
            text_color="gray",
        )
        archived_header.pack(pady=(0, 10), anchor="w", padx=20)

        # Archived goals
        for goal in archived_goals:
            archived_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            archived_frame.pack(fill="x", pady=2, padx=30)

            archived_content = ctk.CTkFrame(archived_frame, fg_color="#F0F0F0", corner_radius=6)
            archived_content.pack(fill="x", padx=5, pady=1)

            archived_label = ctk.CTkLabel(
                archived_content,
                text=goal["name"],
                font=("Arial", 11),
                text_color="gray",
                anchor="w",
            )
            archived_label.pack(side="left", padx=12, pady=8, fill="x", expand=True)

            restore_btn = ctk.CTkButton(
                archived_content,
                text="↺",
                width=25,
                height=20,
                font=("Arial", 9),
                fg_color="#4CAF50",
                command=lambda g=goal: self._restore_goal(g["id"], g["name"]),
            )
            restore_btn.pack(side="right", padx=8, pady=8)

    def _get_archived_goals(self):
        """Get all archived goals."""
        # This would need to be added to GoalManager
        # For now, return empty list
        return []

    def _add_goal(self):
        """Add a new main goal."""
        self._show_goal_dialog("Add New Goal", "", None)

    def _add_subgoal(self):
        """Add a new subgoal to the selected goal."""
        if self.selected_parent_id:
            parent_name = self._get_goal_name(self.selected_parent_id)
            self._show_goal_dialog(f"Add Sub-goal to '{parent_name}'", "", self.selected_parent_id)

    def _edit_goal(self, goal_id, current_name):
        """Edit an existing goal."""
        parent_id = self._get_goal_parent(goal_id)
        dialog_title = "Edit Goal" if parent_id is None else "Edit Sub-goal"
        self._show_goal_dialog(dialog_title, current_name, parent_id, goal_id)

    def _show_goal_dialog(self, title, current_name, parent_id, edit_goal_id=None):
        """Show dialog for adding/editing goals."""
        # Create dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self)  # Make dialog transient to parent
        dialog.grab_set()       # Make dialog modal
        
        # Center on parent
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 200) // 2
        dialog.geometry(f"400x200+{x}+{y}")

        # Ensure dialog is on top and focused
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.focus_force()

        # Content
        ctk.CTkLabel(dialog, text="Goal Name:", font=("Arial", 12)).pack(pady=(20, 5))

        name_var = ctk.StringVar(value=current_name)
        name_entry = ctk.CTkEntry(dialog, textvariable=name_var, width=300, font=("Arial", 11))
        name_entry.pack(pady=5)
        name_entry.focus_set()

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(20, 0))

        def save_goal():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Goal name cannot be empty!")
                return

            try:
                if edit_goal_id:
                    self.goal_manager.update_goal_name(edit_goal_id, name)
                else:
                    self.goal_manager.create_goal(name, parent_id)

                dialog.destroy()
                self._load_goals()  # Refresh display

                if self.on_update_callback:
                    self.on_update_callback()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save goal: {str(e)}")

        def cancel():
            dialog.destroy()

        ctk.CTkButton(btn_frame, text="Cancel", width=80, command=cancel).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Save", width=80, command=save_goal).pack(
            side="right", padx=10
        )

        # Bind Enter key
        name_entry.bind("<Return>", lambda e: save_goal())
        name_entry.bind("<Escape>", lambda e: cancel())

    def _archive_goal(self, goal_id, goal_name):
        """Archive a goal."""
        if messagebox.askyesno(
            "Archive Goal",
            f"Are you sure you want to archive '{goal_name}'?\n\nIt will be moved to the archived section and won't appear in daily focus selection.",
        ):
            self.goal_manager.archive_goal(goal_id)
            self._load_goals()

            if self.on_update_callback:
                self.on_update_callback()

    def _restore_goal(self, goal_id, goal_name):
        """Restore an archived goal."""
        self.goal_manager.restore_goal(goal_id)
        self._load_goals()

        if self.on_update_callback:
            self.on_update_callback()

    def _get_goal_name(self, goal_id):
        """Get goal name by ID (helper method)."""
        goals = self.goal_manager.get_active_goals()
        for goal in goals:
            if goal["id"] == goal_id:
                return goal["name"]
        return "Unknown Goal"

    def _get_goal_parent(self, goal_id):
        """Get parent ID of a goal (helper method)."""
        goals = self.goal_manager.get_active_goals()
        for goal in goals:
            if goal["id"] == goal_id:
                return goal.get("parent_id")
        return None

    def _clear_content_frame(self):
        """Clear all widgets from content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _on_close(self):
        """Handle window close."""
        self.destroy()
