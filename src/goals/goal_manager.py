"""Goal management core logic for Stay-On-Track."""

import datetime
from typing import List, Dict, Optional, Any


class GoalManager:
    """Manages goals, daily focus, and goal-related operations."""

    def __init__(self, storage_manager):
        self.storage = storage_manager

    # =========================================================================
    # Goal CRUD Operations
    # =========================================================================

    def create_goal(self, name: str, parent_id: Optional[int] = None) -> int:
        """Create a new goal."""
        return self.storage.create_goal(name, parent_id)

    def get_active_goals(self) -> List[Dict[str, Any]]:
        """Get all active goals with their subgoals."""
        goals = self.storage.get_active_goals()
        # Add subgoals to each goal
        for goal in goals:
            goal["subgoals"] = self.storage.get_subgoals(goal["id"])
        return goals

    def get_goal_hierarchy(self) -> List[Dict[str, Any]]:
        """Get goals organized in hierarchy."""
        goals = self.get_active_goals()
        # Separate main goals from subgoals
        main_goals = [g for g in goals if g["parent_id"] is None]
        for goal in main_goals:
            goal["subgoals"] = [g for g in goals if g["parent_id"] == goal["id"]]
        return main_goals

    def archive_goal(self, goal_id: int) -> None:
        """Archive a goal (soft delete)."""
        self.storage.archive_goal(goal_id)

    def restore_goal(self, goal_id: int) -> None:
        """Restore an archived goal."""
        self.storage.restore_goal(goal_id)

    def update_goal_name(self, goal_id: int, new_name: str) -> None:
        """Update a goal's name."""
        self.storage.update_goal_name(goal_id, new_name)

    def has_any_goals(self) -> bool:
        """Check if any goals exist (for first-time setup detection)."""
        return self.storage.has_any_goals()

    # =========================================================================
    # Daily Focus Management
    # =========================================================================

    def set_daily_focus(self, goals: List[Dict[str, Any]]) -> None:
        """
        Set daily focus goals for today.
        goals: list of dicts with 'goal_id' (optional) and 'adhoc_name' (optional)
        """
        today = datetime.date.today()
        self.storage.set_daily_focus(today, goals)

    def get_daily_focus_today(self) -> List[Dict[str, Any]]:
        """Get today's daily focus goals."""
        today = datetime.date.today()
        return self.storage.get_daily_focus(today)

    def has_daily_focus_today(self) -> bool:
        """Check if daily focus is set for today."""
        return self.storage.has_daily_focus_today()

    def get_daily_focus_suggestions(self) -> List[str]:
        """Get recent adhoc goals as suggestions for daily focus."""
        return self.storage.get_recent_adhoc_goals(days=7)

    def cleanup_old_adhoc_goals(self) -> None:
        """Clean up adhoc goals older than 7 days."""
        self.storage.cleanup_old_adhoc_goals(days=7)

    # =========================================================================
    # Activity-Goal Linking
    # =========================================================================

    def link_activity_to_goal(self, entry_id: int, goal_id: Optional[int]) -> None:
        """Link an activity entry to a goal (or remove link if goal_id is None)."""
        self.storage.link_activity_to_goal(entry_id, goal_id)

    def get_activities_for_goal(
        self, goal_id: int, date: Optional[datetime.date] = None
    ) -> List[Dict[str, Any]]:
        """Get activities linked to a goal."""
        return self.storage.get_activities_for_goal(goal_id, date)

    def get_goal_progress(self, goal_id: int, days: int = 7) -> Dict[str, Any]:
        """Get progress data for a goal over the last N days."""
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days - 1)
        return self.storage.get_goal_progress(goal_id, start_date, end_date)

    def get_all_goals_progress(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get progress data for all active goals."""
        goals = self.get_active_goals()
        progress_data = []

        for goal in goals:
            progress = self.get_goal_progress(goal["id"], days)
            progress["goal_name"] = goal["name"]
            progress["goal_id"] = goal["id"]
            progress_data.append(progress)

        return sorted(progress_data, key=lambda x: x["time_minutes"], reverse=True)

    # =========================================================================
    # Goal Analytics
    # =========================================================================

    def get_goal_effectiveness_stats(self, goal_id: int, days: int = 7) -> Dict[str, Any]:
        """Get effectiveness statistics for a goal."""
        activities = []
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days - 1)

        current_date = start_date
        while current_date <= end_date:
            activities.extend(self.get_activities_for_goal(goal_id, current_date))
            current_date += datetime.timedelta(days=1)

        total = len(activities)
        if total == 0:
            return {
                "total_activities": 0,
                "good_percentage": 0,
                "bad_percentage": 0,
                "unrated_percentage": 100,
            }

        good_count = sum(1 for a in activities if a["effectiveness"] == "good")
        bad_count = sum(1 for a in activities if a["effectiveness"] == "bad")
        unrated_count = total - good_count - bad_count

        return {
            "total_activities": total,
            "good_percentage": round(good_count / total * 100, 1),
            "bad_percentage": round(bad_count / total * 100, 1),
            "unrated_percentage": round(unrated_count / total * 100, 1),
        }

    def get_goals_comparison(self, days: int = 7) -> Dict[str, Any]:
        """Compare goal performance across all goals."""
        progress_data = self.get_all_goals_progress(days)

        if not progress_data:
            return {
                "total_time": 0,
                "most_productive_goal": None,
                "goal_distribution": {},
            }

        total_time = sum(p["time_minutes"] for p in progress_data)
        most_productive = max(progress_data, key=lambda x: x["time_minutes"])

        # Calculate distribution
        distribution = {}
        for progress in progress_data:
            if total_time > 0:
                percentage = round(progress["time_minutes"] / total_time * 100, 1)
                distribution[progress["goal_name"]] = {
                    "time_minutes": progress["time_minutes"],
                    "percentage": percentage,
                    "activities": progress["activities"],
                }

        return {
            "total_time": total_time,
            "most_productive_goal": most_productive["goal_name"]
            if most_productive["time_minutes"] > 0
            else None,
            "goal_distribution": distribution,
        }

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def format_duration(self, minutes: int) -> str:
        """Format minutes into human-readable duration."""
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours}h"
        return f"{hours}h {remaining_minutes}m"

    def get_goal_suggestions_for_activity(self, activity_text: str) -> List[Dict[str, Any]]:
        """
        Suggest goals based on activity text keywords.
        This is a simple keyword-based suggestion system.
        """
        text_lower = activity_text.lower()
        daily_focus = self.get_daily_focus_today()

        suggestions = []

        # Check daily focus goals first
        for focus in daily_focus:
            if focus["goal_name"]:
                goal_name_lower = focus["goal_name"].lower()
                # Simple keyword matching
                if any(word in text_lower for word in goal_name_lower.split()):
                    suggestions.append(
                        {
                            "goal_id": focus["goal_id"],
                            "goal_name": focus["goal_name"],
                            "reason": "Daily focus match",
                            "priority": 1,  # High priority
                        }
                    )

        # If no matches, suggest all daily focus goals
        if not suggestions:
            for focus in daily_focus:
                if focus["goal_name"]:
                    suggestions.append(
                        {
                            "goal_id": focus["goal_id"],
                            "goal_name": focus["goal_name"],
                            "reason": "Daily focus goal",
                            "priority": 2,  # Medium priority
                        }
                    )

        return sorted(suggestions, key=lambda x: x["priority"])
