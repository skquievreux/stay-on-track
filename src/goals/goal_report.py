"""Goal report export functionality for Stay-On-Track."""

import csv
import datetime
import os
from typing import Any, Dict, List


class GoalReportExporter:
    """Exports goal progress reports to CSV."""

    def __init__(self, goal_manager, storage_manager):
        self.goal_manager = goal_manager
        self.storage_manager = storage_manager

    def export_goal_report(
        self, start_date: datetime.date, end_date: datetime.date, output_path: str = None
    ) -> str:
        """
        Export a comprehensive goal report to CSV.

        Args:
            start_date: Start date for the report
            end_date: End date for the report
            output_path: Optional custom output path

        Returns:
            Path to the generated CSV file
        """
        if not output_path:
            # Default to Documents/StayOnTrack directory
            docs_dir = os.path.expanduser("~/Documents/StayOnTrack")
            os.makedirs(docs_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(docs_dir, f"goal_report_{timestamp}.csv")

        # Collect data
        report_data = self._collect_report_data(start_date, end_date)

        # Write CSV
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Goal Name",
                "Goal Type",
                "Total Time (minutes)",
                "Total Time (formatted)",
                "Activities Count",
                "Good Effectiveness",
                "Bad Effectiveness",
                "Unrated Effectiveness",
                "Effectiveness %",
                "Days Active",
                "Avg Time per Day",
                "Most Productive Day",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for goal_data in report_data:
                writer.writerow(goal_data)

        return output_path

    def _collect_report_data(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> List[Dict[str, Any]]:
        """Collect comprehensive goal data for the report."""
        goals = self.goal_manager.get_active_goals()
        report_data = []

        for goal in goals:
            goal_progress = self._calculate_detailed_goal_progress(goal, start_date, end_date)

            if goal_progress["total_activities"] > 0:  # Only include goals with activity
                report_data.append(
                    {
                        "Goal Name": goal["name"],
                        "Goal Type": "Sub-goal" if goal.get("parent_id") else "Main Goal",
                        "Total Time (minutes)": goal_progress["total_time_minutes"],
                        "Total Time (formatted)": self.goal_manager.format_duration(
                            goal_progress["total_time_minutes"]
                        ),
                        "Activities Count": goal_progress["total_activities"],
                        "Good Effectiveness": goal_progress["good_count"],
                        "Bad Effectiveness": goal_progress["bad_count"],
                        "Unrated Effectiveness": goal_progress["unrated_count"],
                        "Effectiveness %": goal_progress["effectiveness_percentage"],
                        "Days Active": goal_progress["days_active"],
                        "Avg Time per Day": round(goal_progress["avg_time_per_day"], 1),
                        "Most Productive Day": goal_progress["most_productive_day"],
                    }
                )

        # Sort by total time (descending)
        report_data.sort(key=lambda x: x["Total Time (minutes)"], reverse=True)

        return report_data

    def _calculate_detailed_goal_progress(
        self, goal: Dict[str, Any], start_date: datetime.date, end_date: datetime.date
    ) -> Dict[str, Any]:
        """Calculate detailed progress metrics for a goal."""
        activities = []
        daily_totals = {}

        # Collect all activities for this goal
        current_date = start_date
        while current_date <= end_date:
            day_activities = self.goal_manager.get_activities_for_goal(goal["id"], current_date)
            activities.extend(day_activities)

            # Track daily totals
            day_minutes = len(day_activities) * 15
            if day_minutes > 0:
                daily_totals[current_date] = day_minutes

            current_date += datetime.timedelta(days=1)

        total_activities = len(activities)
        total_time_minutes = total_activities * 15

        # Effectiveness stats
        good_count = sum(1 for a in activities if a["effectiveness"] == "good")
        bad_count = sum(1 for a in activities if a["effectiveness"] == "bad")
        unrated_count = total_activities - good_count - bad_count

        effectiveness_percentage = (
            round(good_count / total_activities * 100, 1) if total_activities > 0 else 0
        )

        # Daily activity stats
        days_active = len(daily_totals)
        avg_time_per_day = total_time_minutes / days_active if days_active > 0 else 0

        # Most productive day
        most_productive_day = (
            max(daily_totals.items(), key=lambda x: x[1]) if daily_totals else (None, 0)
        )
        most_productive_day_str = (
            most_productive_day[0].strftime("%Y-%m-%d") if most_productive_day[0] else "N/A"
        )

        return {
            "total_activities": total_activities,
            "total_time_minutes": total_time_minutes,
            "good_count": good_count,
            "bad_count": bad_count,
            "unrated_count": unrated_count,
            "effectiveness_percentage": effectiveness_percentage,
            "days_active": days_active,
            "avg_time_per_day": avg_time_per_day,
            "most_productive_day": most_productive_day_str,
        }

    def export_weekly_summary(self, output_path: str = None) -> str:
        """Export a weekly goal summary (last 7 days)."""
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=6)
        return self.export_goal_report(start_date, end_date, output_path)

    def export_monthly_summary(self, output_path: str = None) -> str:
        """Export a monthly goal summary (last 30 days)."""
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=29)
        return self.export_goal_report(start_date, end_date, output_path)
