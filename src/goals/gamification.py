"""Gamification features for Stay-On-Track: streaks, achievements, and motivation."""

import datetime
from typing import Any, Dict, List, Optional


class GamificationManager:
    """Manages streaks, achievements, and motivational content."""

    def __init__(self, storage_manager):
        self.storage = storage_manager

    # =========================================================================
    # Streak Management
    # =========================================================================

    def update_streak(self, date: Optional[datetime.date] = None) -> None:
        """Update streak based on goal-related activities."""
        if date is None:
            date = datetime.date.today()
        self.storage.update_streak(date)

    def get_current_streak(self) -> int:
        """Get the current active streak length."""
        return self.storage.get_current_streak()

    def get_longest_streak(self) -> int:
        """Get the longest streak ever achieved."""
        return self.storage.get_longest_streak()

    def get_streak_info(self) -> Dict[str, Any]:
        """Get comprehensive streak information."""
        current = self.get_current_streak()
        longest = self.get_longest_streak()

        # Calculate streak milestones
        milestones = [3, 7, 14, 30, 60, 90, 180, 365]
        next_milestone = next((m for m in milestones if m > current), None)

        return {
            "current": current,
            "longest": longest,
            "next_milestone": next_milestone,
            "progress_to_next": current / next_milestone if next_milestone else 1.0,
        }

    # =========================================================================
    # Achievement System
    # =========================================================================

    ACHIEVEMENTS = {
        "first_steps": {
            "name": "First Steps",
            "description": "Link your first activity to a goal",
            "icon": "🌱",
            "condition": "first_goal_link",
        },
        "on_fire": {
            "name": "On Fire",
            "description": "Maintain a 7-day streak",
            "icon": "🔥",
            "condition": "streak_7",
        },
        "laser_focus": {
            "name": "Laser Focus",
            "description": "100% of activities linked to goals in a day",
            "icon": "🎯",
            "condition": "perfect_day",
        },
        "consistency": {
            "name": "Consistency Champion",
            "description": "Maintain a 30-day streak",
            "icon": "📈",
            "condition": "streak_30",
        },
        "goal_crusher": {
            "name": "Goal Crusher",
            "description": "Link 50 activities to a single goal",
            "icon": "💪",
            "condition": "goal_50_activities",
        },
        "early_bird": {
            "name": "Early Bird",
            "description": "Set daily focus before 8 AM",
            "icon": "🐦",
            "condition": "early_focus",
        },
        "reflection": {
            "name": "Reflective Thinker",
            "description": "View analytics 10 times",
            "icon": "🤔",
            "condition": "analytics_views_10",
        },
        "perfectionist": {
            "name": "Perfectionist",
            "description": "Rate 50 activities as effective",
            "icon": "⭐",
            "condition": "effective_50",
        },
    }

    def check_and_unlock_achievements(self) -> List[str]:
        """
        Check all achievement conditions and unlock new ones.
        Returns list of newly unlocked achievement keys.
        """
        newly_unlocked = []

        # Check each achievement
        for key, _achievement in self.ACHIEVEMENTS.items():
            if self._check_achievement_condition(key):
                if self.storage.unlock_achievement(key):
                    newly_unlocked.append(key)

        return newly_unlocked

    def _check_achievement_condition(self, achievement_key: str) -> bool:
        """Check if an achievement condition is met."""
        if achievement_key == "first_goal_link":
            # Check if any activity is linked to a goal
            with self.storage._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM entries WHERE goal_id IS NOT NULL")
                row = cursor.fetchone()
                return row["count"] > 0

        elif achievement_key == "streak_7":
            return self.get_current_streak() >= 7

        elif achievement_key == "streak_30":
            return self.get_current_streak() >= 30

        elif achievement_key == "perfect_day":
            # Check if today has 100% goal-linked activities
            today = datetime.date.today()
            entries = self.storage.get_today_entries()
            if not entries:
                return False
            goal_linked = sum(1 for e in entries if e.get("goal_id") is not None)
            return goal_linked == len(entries)

        elif achievement_key == "goal_50_activities":
            # Check if any goal has 50+ activities
            goals = self.storage.get_active_goals()
            for goal in goals:
                activities = self.storage.get_activities_for_goal(goal["id"])
                if len(activities) >= 50:
                    return True
            return False

        elif achievement_key == "early_focus":
            # Check if daily focus was set before 8 AM today
            today = datetime.date.today()
            daily_focus = self.storage.get_daily_focus(today)
            if not daily_focus:
                return False

            # Check creation time (assuming first entry represents set time)
            with self.storage._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT created_at FROM daily_focus WHERE date = ? ORDER BY created_at ASC LIMIT 1",
                    (today.isoformat(),),
                )
                row = cursor.fetchone()
                if row:
                    created_time = datetime.datetime.fromisoformat(row["created_at"]).time()
                    return created_time.hour < 8
            return False

        elif achievement_key == "analytics_views_10":
            # This would need to be tracked separately - for now, return False
            # In a real implementation, you'd track analytics views in a separate table
            return False

        elif achievement_key == "effective_50":
            # Check if 50+ activities are rated as effective
            with self.storage._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM entries WHERE effectiveness = 'good'")
                row = cursor.fetchone()
                return row["count"] >= 50

        return False

    def get_unlocked_achievements(self) -> List[Dict[str, Any]]:
        """Get all unlocked achievements with metadata."""
        unlocked = self.storage.get_unlocked_achievements()
        result = []

        for achievement in unlocked:
            key = achievement["key"]
            if key in self.ACHIEVEMENTS:
                metadata = self.ACHIEVEMENTS[key].copy()
                metadata["unlocked_at"] = achievement["unlocked_at"]
                result.append(metadata)

        return result

    def get_pending_notifications(self) -> List[Dict[str, Any]]:
        """Get achievements that need to be notified to the user."""
        pending = self.storage.get_pending_achievement_notifications()
        result = []

        for item in pending:
            key = item["key"]
            if key in self.ACHIEVEMENTS:
                metadata = self.ACHIEVEMENTS[key].copy()
                metadata["id"] = item["id"]
                result.append(metadata)

        return result

    def mark_achievement_notified(self, achievement_id: int) -> None:
        """Mark an achievement as notified."""
        self.storage.mark_achievement_notified(achievement_id)

    # =========================================================================
    # Motivational Quotes
    # =========================================================================

    MORNING_QUOTES = [
        "Small daily improvements lead to stunning results.",
        "Your habits shape your future.",
        "Every hour invested in yourself pays dividends.",
        "Focus on progress, not perfection.",
        "The best time to start was yesterday. The next best time is now.",
        "Consistency beats intensity.",
        "Your goals don't care about your excuses.",
        "Master your minutes, master your life.",
        "Action creates clarity.",
        "Invest in yourself first.",
        "Today matters more than you think.",
        "Small steps lead to big changes.",
        "Your future self will thank you.",
        "Discipline is choosing between what you want now and what you want most.",
        "The compound effect of daily habits is extraordinary.",
    ]

    EVENING_QUOTES = [
        "Discipline is the bridge between goals and results.",
        "Progress requires focus.",
        "Today's choices become tomorrow's reality.",
        "Reflect, learn, improve.",
        "Every day is a chance to get better.",
        "Success is the sum of small efforts repeated daily.",
        "You are the architect of your own destiny.",
        "Growth happens outside your comfort zone.",
        "Celebrate progress, not perfection.",
        "Rest well, tomorrow brings new opportunities.",
        "Your efforts today create your success tomorrow.",
        "Reflection turns experience into insight.",
        "End strong, start stronger.",
        "Consistency creates momentum.",
        "Tomorrow's achievements are built on today's discipline.",
    ]

    def get_morning_quote(self) -> str:
        """Get a random morning motivational quote."""
        # Use date-based pseudo-random selection for consistency
        today = datetime.date.today()
        index = today.toordinal() % len(self.MORNING_QUOTES)
        return self.MORNING_QUOTES[index]

    def get_evening_quote(self) -> str:
        """Get a random evening motivational quote."""
        # Use date-based pseudo-random selection for consistency
        today = datetime.date.today()
        index = today.toordinal() % len(self.EVENING_QUOTES)
        return self.EVENING_QUOTES[index]

    def get_quote_for_time(self) -> str:
        """Get appropriate quote based on current time."""
        now = datetime.datetime.now().time()
        morning_end = datetime.time(12, 0)  # Before noon = morning
        evening_start = datetime.time(17, 0)  # After 5 PM = evening

        if now < morning_end:
            return self.get_morning_quote()
        elif now > evening_start:
            return self.get_evening_quote()
        else:
            # Afternoon - mix of both
            quotes = self.MORNING_QUOTES + self.EVENING_QUOTES
            index = datetime.date.today().toordinal() % len(quotes)
            return quotes[index]

    # =========================================================================
    # Gamification Analytics
    # =========================================================================

    def get_gamification_stats(self) -> Dict[str, Any]:
        """Get comprehensive gamification statistics."""
        streak_info = self.get_streak_info()
        unlocked_achievements = self.get_unlocked_achievements()

        # Calculate achievement completion rate
        total_achievements = len(self.ACHIEVEMENTS)
        unlocked_count = len(unlocked_achievements)
        completion_rate = round(unlocked_count / total_achievements * 100, 1)

        # Get recent achievements (last 30 days)
        thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        recent_achievements = [
            a for a in unlocked_achievements if a["unlocked_at"] > thirty_days_ago
        ]

        return {
            "streak": streak_info,
            "achievements": {
                "unlocked": unlocked_count,
                "total": total_achievements,
                "completion_rate": completion_rate,
                "recent": recent_achievements,
            },
            "motivation": {
                "current_quote": self.get_quote_for_time(),
            },
        }
