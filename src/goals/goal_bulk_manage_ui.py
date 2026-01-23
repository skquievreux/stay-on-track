"""Improved goal management interface for Stay-On-Track."""

import customtkinter as ctk
from tkinter import messagebox
from typing import Any, Dict, List, Optional


class GoalBulkManageWindow(ctk.CTkToplevel):
    """
    Advanced window for managing goals with hierarchical view, 
    bulk actions, and activity assignment.
    """

    def __init__(self, goal_manager, on_update_callback=None):
        super().__init__()
        self.goal_manager = goal_manager
        self.on_update_callback = on_update_callback

        # State
        self.selected_goal_ids = set()
        self.goal_vars = {}

        # Configure window
        self.title("🎯 Goal Management - Stay On Track")
        self.geometry("900x700")
        self.attributes("-topmost", True)
        self.minsize(800, 600)

        # Initialize UI
        self._create_main_layout()
        self._load_goals()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

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
            elif target == "history":
                parent.open_history()
            self.destroy()

    def _create_main_layout(self):
        """Create the split-view layout."""
        # Navigation Bar (Central Header)
        self.nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_bar.pack(fill="x", padx=30, pady=(10, 0))
        
        self._create_nav_button(self.nav_bar, "📋 Log", lambda: self._switch_to("history")).pack(side="left", expand=True, padx=2)
        self._create_nav_button(self.nav_bar, "📊 Analytics", lambda: self._switch_to("analytics")).pack(side="left", expand=True, padx=2)
        self._create_nav_button(self.nav_bar, "🎯 Goals", "current").pack(side="left", expand=True, padx=2)

        # Top title area
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 10), padx=30)
        
        ctk.CTkLabel(
            header_frame, 
            text="🎯 Goal Management", 
            font=("Arial", 24, "bold")
        ).pack(side="left")

        # Main content area (Split View)
        self.paned_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.paned_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Left Column: Goal Tree View
        self.left_column = ctk.CTkFrame(self.paned_frame, width=450)
        self.left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            self.left_column, 
            text="📋 All Goals", 
            font=("Arial", 16, "bold"),
            anchor="w"
        ).pack(pady=10, padx=20, fill="x")

        self.tree_frame = ctk.CTkScrollableFrame(self.left_column, fg_color="transparent")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Right Column: Tools
        self.right_column = ctk.CTkFrame(self.paned_frame, width=350)
        self.right_column.pack(side="right", fill="both", padx=(10, 0))

        # 1. Quick Add Section
        self._create_quick_add_ui()
        
        # 2. Bulk Import Section
        self._create_bulk_import_ui()
        
        # 3. Selection Summary
        self._create_selection_summary_ui()

        # Bottom Action Bar
        self.action_bar = ctk.CTkFrame(self, height=80, fg_color="transparent")
        self.action_bar.pack(fill="x", pady=(10, 20), padx=30)

        self.assign_btn = ctk.CTkButton(
            self.action_bar,
            text="📊 Assign to Activities",
            font=("Arial", 13, "bold"),
            fg_color="#4CAF50",
            hover_color="#388E3C",
            height=40,
            command=self._assign_to_activities
        )
        self.assign_btn.pack(side="right", padx=10)

        ctk.CTkButton(
            self.action_bar,
            text="Close",
            width=100,
            height=40,
            fg_color="#F5F5F5",
            text_color="#333333",
            hover_color="#E0E0E0",
            command=self._on_close
        ).pack(side="right", padx=10)

    def _create_quick_add_ui(self):
        """Create the Quick Add section in the right column."""
        qa_frame = ctk.CTkFrame(self.right_column, fg_color="transparent")
        qa_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            qa_frame, 
            text="➕ Quick Add", 
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(qa_frame, text="Goal Name:", font=("Arial", 11)).pack(anchor="w")
        self.qa_name_entry = ctk.CTkEntry(qa_frame, placeholder_text="e.g., Python Mastery")
        self.qa_name_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(qa_frame, text="Parent Goal:", font=("Arial", 11)).pack(anchor="w")
        self.qa_parent_var = ctk.StringVar(value="None")
        self.qa_parent_menu = ctk.CTkOptionMenu(
            qa_frame, 
            variable=self.qa_parent_var,
            values=["None"]
        )
        self.qa_parent_menu.pack(fill="x", pady=(0, 15))

        self.qa_add_btn = ctk.CTkButton(
            qa_frame, 
            text="+ Add Goal", 
            command=self._quick_add_goal
        )
        self.qa_add_btn.pack(fill="x")

    def _create_bulk_import_ui(self):
        """Create the Bulk Import section in the right column."""
        bi_frame = ctk.CTkFrame(self.right_column, fg_color="transparent")
        bi_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            bi_frame, 
            text="📥 Bulk Import", 
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            bi_frame, 
            text="One goal per line. Use '-' for subgoals.", 
            font=("Arial", 10),
            text_color="gray",
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        self.bi_text = ctk.CTkTextbox(bi_frame, height=150)
        self.bi_text.pack(fill="both", expand=True, pady=(0, 10))
        self.bi_text.insert("1.0", "Main Project\n- Requirement 1\n- Requirement 2\nAnother Goal")

        self.bi_import_btn = ctk.CTkButton(
            bi_frame, 
            text="Import Goals", 
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=self._bulk_import
        )
        self.bi_import_btn.pack(fill="x")

    def _create_selection_summary_ui(self):
        """Create the selection summary box."""
        self.summary_frame = ctk.CTkFrame(self.right_column, fg_color="#E3F2FD", corner_radius=10)
        self.summary_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.summary_label = ctk.CTkLabel(
            self.summary_frame,
            text="Selected for Activity Assignment: 0 goals",
            font=("Arial", 11, "bold"),
            text_color="#1976D2",
            wraplength=250
        )
        self.summary_label.pack(pady=15, padx=15)

    def _load_goals(self):
        """Load goals and populate the tree view and dropdown."""
        # Clear tree
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        
        self.goal_vars = {}
        
        hierarchy = self.goal_manager.get_goal_hierarchy()
        archived = self.goal_manager.get_archived_goals()
        
        # Populate Tree with Active Goals
        if not hierarchy and not archived:
            ctk.CTkLabel(
                self.tree_frame, 
                text="No goals yet. Use the tools on the right!",
                text_color="gray"
            ).pack(pady=50)
        else:
            if hierarchy:
                for goal in hierarchy:
                    self._create_tree_item(goal, level=0)
            
            # Archived Section
            if archived:
                self._create_archived_section(archived)
        
        # Update Parent Menu
        self.active_main_goal_names = ["None"] + [g["name"] for g in hierarchy]
        self.qa_parent_menu.configure(values=self.active_main_goal_names)
        
        self._update_selection_summary()

    def _create_tree_item(self, goal: Dict, level: int):
        """Create a hierarchical item in the tree view."""
        item_frame = ctk.CTkFrame(self.tree_frame, fg_color="transparent")
        item_frame.pack(fill="x", pady=2)
        
        # Indentation
        indent_width = level * 30
        ctk.CTkFrame(item_frame, width=indent_width, height=1, fg_color="transparent").pack(side="left")
        
        # Checkbox
        var = ctk.BooleanVar(value=goal["id"] in self.selected_goal_ids)
        self.goal_vars[goal["id"]] = var
        
        cb = ctk.CTkCheckBox(
            item_frame,
            text="",
            variable=var,
            width=24,
            command=lambda g_id=goal["id"]: self._toggle_selection(g_id)
        )
        cb.pack(side="left", padx=(5, 5))
        
        # Goal Name (as a button for parent selection)
        name_btn = ctk.CTkButton(
            item_frame,
            text=f"{'🎯 ' if level == 0 else '└─ '}{goal['name']}",
            font=("Arial", 12 if level == 0 else 11, "bold" if level == 0 else "normal"),
            anchor="w",
            fg_color="transparent",
            text_color="#333333",
            hover_color="#E0E0E0",
            height=28,
            command=lambda g=goal: self._select_as_parent(g["name"])
        )
        name_btn.pack(side="left", fill="x", expand=True)
        
        # Actions
        actions = ctk.CTkFrame(item_frame, fg_color="transparent")
        actions.pack(side="right", padx=10)
        
        ctk.CTkButton(
            actions, text="✎", width=25, height=25, 
            command=lambda g=goal: self._edit_goal(g["id"], g["name"])
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            actions, text="🗂️", width=25, height=25, fg_color="#FF9800",
            command=lambda g=goal: self._archive_goal(g["id"], g["name"])
        ).pack(side="left", padx=2)

        # Process subgoals
        if goal.get("subgoals"):
            for sub in goal["subgoals"]:
                self._create_tree_item(sub, level + 1)

    def _create_archived_section(self, archived_goals):
        """Create a collapsible section for archived goals."""
        ctk.CTkFrame(self.tree_frame, height=2, fg_color="#DDDDDD").pack(fill="x", pady=(20, 10), padx=20)
        
        ctk.CTkLabel(
            self.tree_frame, 
            text="📦 Archived Goals", 
            font=("Arial", 13, "bold"),
            text_color="gray"
        ).pack(pady=(0, 10), padx=20, anchor="w")

        for goal in archived_goals:
            item_frame = ctk.CTkFrame(self.tree_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=1, padx=20)
            
            ctk.CTkLabel(
                item_frame, 
                text=goal["name"], 
                font=("Arial", 11),
                text_color="gray",
                anchor="w"
            ).pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                item_frame, 
                text="↺ Restore", 
                width=80, 
                height=24,
                font=("Arial", 10),
                fg_color="#4CAF50",
                command=lambda g=goal: self._restore_goal(g["id"], g["name"])
            ).pack(side="right", padx=5)

    def _select_as_parent(self, name: str):
        """Set the Quick Add parent dropdown to this goal's name."""
        if name in self.qa_parent_menu.cget("values"):
            self.qa_parent_var.set(name)
        else:
            # If it's a subgoal, we might want to select its parent instead, 
            # but usually only main goals are parents in this simple UI.
            # For now, we only set it if it exists in the menu.
            pass

    def _restore_goal(self, goal_id: int, name: str):
        """Restore an archived goal."""
        self.goal_manager.restore_goal(goal_id)
        self._load_goals()
        if self.on_update_callback:
            self.on_update_callback()

    def _toggle_selection(self, goal_id: int):
        """Update the set of selected IDs based on checkbox."""
        if self.goal_vars[goal_id].get():
            self.selected_goal_ids.add(goal_id)
        else:
            self.selected_goal_ids.discard(goal_id)
        self._update_selection_summary()

    def _update_selection_summary(self):
        """Update the text in the summary box."""
        count = len(self.selected_goal_ids)
        self.summary_label.configure(
            text=f"Selected for Activity Assignment: {count} goals"
        )
        
        if count > 0:
            self.assign_btn.configure(state="normal", fg_color="#4CAF50")
        else:
            self.assign_btn.configure(state="disabled", fg_color="#A5D6A7")

    def _quick_add_goal(self):
        """Add a single goal from the Quick Add panel."""
        name = self.qa_name_entry.get().strip()
        if not name:
            return
            
        parent_name = self.qa_parent_var.get()
        parent_id = None
        
        if parent_name != "None":
            # Find parent ID
            hierarchy = self.goal_manager.get_goal_hierarchy()
            for g in hierarchy:
                if g["name"] == parent_name:
                    parent_id = g["id"]
                    break
        
        try:
            self.goal_manager.create_goal(name, parent_id)
            self.qa_name_entry.delete(0, "end")
            self._load_goals()
            if self.on_update_callback:
                self.on_update_callback()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add goal: {e}")

    def _bulk_import(self):
        """Import multiple goals from the text box."""
        text = self.bi_text.get("1.0", "end-1c").strip()
        if not text:
            return
            
        lines = text.split("\n")
        goals_to_create = []
        current_parent_id = None
        
        try:
            # Simple hierarchical parser: lines starting with '-' are subgoals of the previous main goal
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("-"):
                    name = line[1:].strip()
                    if current_parent_id is None:
                        # No parent yet, make it a main goal anyway or ignore '-'
                        current_parent_id = self.goal_manager.create_goal(name)
                    else:
                        self.goal_manager.create_goal(name, current_parent_id)
                else:
                    name = line
                    current_parent_id = self.goal_manager.create_goal(name)
            
            self.bi_text.delete("1.0", "end")
            self._load_goals()
            if self.on_update_callback:
                self.on_update_callback()
            messagebox.showinfo("Success", "Goals imported successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")

    def _edit_goal(self, goal_id: int, current_name: str):
        """Simple edit dialog (re-using logic or inline - keeping it simple for now)."""
        new_name = ctk.CTkInputDialog(text="New Goal Name:", title="Edit Goal").get_input()
        if new_name and new_name.strip():
            self.goal_manager.update_goal_name(goal_id, new_name.strip())
            self._load_goals()
            if self.on_update_callback:
                self.on_update_callback()

    def _archive_goal(self, goal_id: int, name: str):
        """Archive a goal."""
        if messagebox.askyesno("Archive", f"Archive '{name}'?"):
            self.goal_manager.archive_goal(goal_id)
            self.selected_goal_ids.discard(goal_id)
            self._load_goals()
            if self.on_update_callback:
                self.on_update_callback()

    def _assign_to_activities(self):
        """Convert selected goals to daily focus and close."""
        if not self.selected_goal_ids:
            return
            
        daily_goals = [{"goal_id": g_id} for g_id in self.selected_goal_ids]
        self.goal_manager.set_daily_focus(daily_goals)
        
        messagebox.showinfo(
            "Assigned", 
            f"{len(self.selected_goal_ids)} goals assigned to today's focus!"
        )
        self._on_close()

    def _on_close(self):
        """Handle window close."""
        self.destroy()
