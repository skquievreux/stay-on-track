"""Analytics dashboard UI for Stay-On-Track application."""

import datetime

import customtkinter as ctk

from analytics import AnalyticsEngine
from category_engine import CategoryEngine
from goals.goal_manager import GoalManager
from goals.goal_report import GoalReportExporter


class AnalyticsWindow(ctk.CTkToplevel):
    """Multi-day analytics dashboard"""

    def __init__(self, storage_manager, goal_manager=None):
        super().__init__()
        self.storage_manager = storage_manager
        self.goal_manager = goal_manager
        self.analytics = AnalyticsEngine(storage_manager)
        self.category_engine = CategoryEngine()
        self.goal_report_exporter = (
            GoalReportExporter(goal_manager, storage_manager) if goal_manager else None
        )
        self.days = 7  # Default to last 7 days

        self.title("Analytics Dashboard")
        self.geometry("600x800")
        self.attributes("-topmost", True)

        # Title
        self.lbl_title = ctk.CTkLabel(self, text="Activity Analytics", font=("Arial", 18, "bold"))
        self.lbl_title.pack(pady=15)

        # Period Selector
        self.period_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.period_frame.pack(pady=10)

        ctk.CTkLabel(self.period_frame, text="Period:", font=("Arial", 12)).pack(
            side="left", padx=5
        )

        self.btn_7days = ctk.CTkButton(
            self.period_frame,
            text="Last 7 Days",
            width=100,
            command=lambda: self._change_period(7),
        )
        self.btn_7days.pack(side="left", padx=5)

        self.btn_30days = ctk.CTkButton(
            self.period_frame,
            text="Last 30 Days",
            width=100,
            command=lambda: self._change_period(30),
        )
        self.btn_30days.pack(side="left", padx=5)

        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=580, height=650)
        self.scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self._load_analytics()

    def _change_period(self, days):
        """Change the analytics period"""
        self.days = days

        # Clear existing content
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self._load_analytics()

    def _load_analytics(self):
        """Load and display analytics"""
        stats = self.analytics.get_overall_stats(self.days)
        summaries = self.analytics.get_week_summary()
        heatmap = self.analytics.get_activity_heatmap(self.days)

        # Summary Section
        summary_frame = ctk.CTkFrame(self.scroll_frame)
        summary_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(
            summary_frame,
            text=f"Summary (Last {self.days} Days)",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Stats Grid
        stats_text = f"""
Total Entries:        {stats["total_entries"]}
Days with Data:       {stats["days_with_data"]}
Avg per Day:          {stats["avg_per_day"]}
Most Productive:      {stats["most_productive_day"]} ({stats["most_productive_count"]} entries)
Most Active Hour:     {stats["most_active_hour"]:02d}:00 ({stats["most_active_hour_count"]} entries)
        """.strip()

        ctk.CTkLabel(summary_frame, text=stats_text, font=("Courier New", 12), justify="left").pack(
            pady=10, padx=20
        )

        # Effectiveness Section (NEW)
        self._create_effectiveness_section(stats)

        # Category Breakdown Section
        self._create_category_breakdown()

        # Goal Progress Section
        if self.goal_manager:
            self._create_goal_progress_section()

        # Daily Breakdown Section
        breakdown_frame = ctk.CTkFrame(self.scroll_frame)
        breakdown_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(breakdown_frame, text="Daily Breakdown", font=("Arial", 14, "bold")).pack(
            pady=10
        )

        # Show only last 7 days for visualization
        recent_summaries = summaries[-7:] if len(summaries) > 7 else summaries

        for summary in reversed(recent_summaries):
            self._create_day_bar(breakdown_frame, summary)

        # Activity Heatmap Section
        if heatmap:
            heatmap_frame = ctk.CTkFrame(self.scroll_frame)
            heatmap_frame.pack(pady=10, padx=10, fill="x")

            ctk.CTkLabel(heatmap_frame, text="Activity by Hour", font=("Arial", 14, "bold")).pack(
                pady=10
            )

            # Show top 5 hours
            sorted_hours = sorted(heatmap.items(), key=lambda x: x[1], reverse=True)[:5]

            for hour, count in sorted_hours:
                hour_text = f"{hour:02d}:00 - {hour:02d}:59"
                bar_length = min(count * 3, 40)
                bar = "|" * bar_length

                row = ctk.CTkFrame(heatmap_frame, fg_color="transparent")
                row.pack(pady=2, padx=10, fill="x")

                ctk.CTkLabel(
                    row,
                    text=f"{hour_text}  {bar}  {count}",
                    font=("Courier New", 11),
                    anchor="w",
                ).pack(side="left")

    def _create_effectiveness_section(self, stats):
        """Create effectiveness statistics section"""
        eff_frame = ctk.CTkFrame(self.scroll_frame)
        eff_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(
            eff_frame,
            text=f"Effectiveness (Last {self.days} Days)",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Get effectiveness stats
        good_count = stats.get("effectiveness_good", 0)
        bad_count = stats.get("effectiveness_bad", 0)
        good_pct = stats.get("effectiveness_good_pct", 0)

        total_rated = good_count + bad_count

        if total_rated == 0:
            ctk.CTkLabel(
                eff_frame,
                text="No effectiveness ratings yet",
                font=("Arial", 11),
                text_color="gray",
            ).pack(pady=5)
            return

        # Visual bars
        stats_container = ctk.CTkFrame(eff_frame, fg_color="transparent")
        stats_container.pack(pady=10, padx=20, fill="x")

        # Good row
        good_row = ctk.CTkFrame(stats_container, fg_color="transparent")
        good_row.pack(fill="x", pady=3)

        ctk.CTkLabel(good_row, text="Good:", width=60, anchor="w", font=("Arial", 11)).pack(
            side="left"
        )

        good_bar_len = min(int(good_pct / 2.5), 40) if good_pct > 0 else 0
        good_bar = "|" * good_bar_len if good_bar_len > 0 else ""

        ctk.CTkLabel(
            good_row,
            text=good_bar,
            font=("Courier New", 11),
            text_color="#4CAF50",
            width=250,
            anchor="w",
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            good_row, text=f"{good_count} ({good_pct}%)", font=("Arial", 11), width=80
        ).pack(side="left")

        # Bad row
        bad_row = ctk.CTkFrame(stats_container, fg_color="transparent")
        bad_row.pack(fill="x", pady=3)

        bad_pct = 100 - good_pct if total_rated > 0 else 0

        ctk.CTkLabel(bad_row, text="Bad:", width=60, anchor="w", font=("Arial", 11)).pack(
            side="left"
        )

        bad_bar_len = min(int(bad_pct / 2.5), 40) if bad_pct > 0 else 0
        bad_bar = "|" * bad_bar_len if bad_bar_len > 0 else ""

        ctk.CTkLabel(
            bad_row,
            text=bad_bar,
            font=("Courier New", 11),
            text_color="#EF5350",
            width=250,
            anchor="w",
        ).pack(side="left", padx=5)

        ctk.CTkLabel(bad_row, text=f"{bad_count} ({bad_pct}%)", font=("Arial", 11), width=80).pack(
            side="left"
        )

    def _create_category_breakdown(self):
        """Create category breakdown visualization"""
        # Get all entries for the period
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=self.days - 1)

        entries_by_date = self.storage_manager.get_date_range_entries(start_date, end_date)

        # Flatten all entries
        all_entries = []
        for _date, day_entries in entries_by_date.items():
            all_entries.extend(day_entries)

        if not all_entries:
            return

        # Get category breakdown
        breakdown = self.category_engine.get_category_breakdown(all_entries)

        if not breakdown:
            return

        # Create frame
        category_frame = ctk.CTkFrame(self.scroll_frame)
        category_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(
            category_frame,
            text=f"Category Breakdown (Last {self.days} Days)",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Create bars for each category
        for category, data in breakdown.items():
            self._create_category_bar(category_frame, category, data)

    def _create_category_bar(self, parent, category, data):
        """Create a visual bar for a category"""
        count = data["count"]
        percentage = data["percentage"]

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(pady=3, padx=10, fill="x")

        # Category label
        ctk.CTkLabel(row, text=category, font=("Arial", 11), width=150, anchor="w").pack(
            side="left", padx=5
        )

        # Visual bar
        bar_length = min(int(percentage / 2), 40)
        bar = "|" * bar_length if bar_length > 0 else "."

        ctk.CTkLabel(
            row,
            text=bar,
            font=("Courier New", 11),
            text_color=self._get_category_color(category),
            anchor="w",
            width=250,
        ).pack(side="left", padx=5)

        # Percentage and count
        ctk.CTkLabel(
            row, text=f"{percentage}% ({count})", font=("Arial", 11), width=80, anchor="e"
        ).pack(side="left", padx=5)

    def _get_category_color(self, category):
        """Get color for category"""
        colors = {
            "Essen": "#FF6B6B",
            "Jobsuche": "#4ECDC4",
            "Meetings": "#95E1D3",
            "Entwicklung": "#F38181",
            "Dokumentation": "#AA96DA",
            "KI/Automation": "#FCBAD3",
            "Lernen": "#FFFFD2",
            "Schreiben": "#A8D8EA",
            "Recherche": "#B4E7CE",
            "Sonstiges": "#CCCCCC",
        }
        # Check if category contains any of the keys
        for key, color in colors.items():
            if key in category:
                return color
        return "gray"

    def _create_day_bar(self, parent, summary):
        """Create a visual bar for a day's activity"""
        date_str = summary["date"].strftime("%Y-%m-%d")
        count = summary["total_entries"]

        # Determine if it's today
        is_today = summary["date"] == datetime.date.today()

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(pady=3, padx=10, fill="x")

        # Date label
        date_label = f"{date_str}{'  (Today)' if is_today else ''}"
        ctk.CTkLabel(
            row, text=f"{time_str} ({percentage}%)", font=("Arial", 11), width=80, anchor="e"
        ).pack(side="left", padx=5)

    def _export_goal_report(self):
        """Export goal report to CSV."""
        if not self.goal_report_exporter:
            return

        try:
            # Calculate date range
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=self.days - 1)

            # Export report
            report_path = self.goal_report_exporter.export_goal_report(start_date, end_date)

            # Show success message
            success_msg = f"Goal report exported successfully!\n\nFile: {report_path}"

            # Create success dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title("Export Successful")
            dialog.geometry("400x150")
            dialog.attributes("-topmost", True)

            ctk.CTkLabel(dialog, text=success_msg, font=("Arial", 11)).pack(pady=20, padx=20)

            ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)

        except Exception as e:
            # Show error message
            error_msg = f"Failed to export goal report:\n\n{str(e)}"

            dialog = ctk.CTkToplevel(self)
            dialog.title("Export Failed")
            dialog.geometry("400x120")
            dialog.attributes("-topmost", True)

            ctk.CTkLabel(dialog, text=error_msg, font=("Arial", 11), text_color="red").pack(
                pady=20, padx=20
            )

            ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)

        # Visual bar
        bar_length = min(count * 2, 40)
        bar = "|" * bar_length if count > 0 else "."

        ctk.CTkLabel(
            row,
            text=bar,
            font=("Courier New", 11),
            text_color="#4CAF50" if is_today else "gray",
            anchor="w",
            width=300,
        ).pack(side="left", padx=5)

        # Count
        ctk.CTkLabel(row, text=str(count), font=("Arial", 11), width=40, anchor="e").pack(
            side="left", padx=5
        )

    def _create_goal_progress_section(self):
        """Create goal progress section."""
        goal_comparison = self.goal_manager.get_goals_comparison(self.days)

        if not goal_comparison["goal_distribution"]:
            return

        # Goal Progress Section
        goal_frame = ctk.CTkFrame(self.scroll_frame)
        goal_frame.pack(pady=10, padx=10, fill="x")

        # Header with export buttons
        header_frame = ctk.CTkFrame(goal_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            header_frame,
            text=f"🎯 Goal Progress (Last {self.days} Days)",
            font=("Arial", 14, "bold"),
        ).pack(side="left")

        # Export buttons
        export_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        export_frame.pack(side="right")

        ctk.CTkButton(
            export_frame,
            text="📊 Export Report",
            width=120,
            height=30,
            font=("Arial", 10),
            command=self._export_goal_report,
        ).pack(side="left", padx=5)

        # Most productive goal
        if goal_comparison["most_productive_goal"]:
            productive_label = ctk.CTkLabel(
                goal_frame,
                text=f"Most Productive: {goal_comparison['most_productive_goal']}",
                font=("Arial", 12, "bold"),
                text_color="#4CAF50",
            )
            productive_label.pack(pady=(0, 10))

        # Goal distribution
        for goal_name, data in goal_comparison["goal_distribution"].items():
            self._create_goal_progress_bar(goal_frame, goal_name, data)

    def _create_goal_progress_bar(self, parent, goal_name, data):
        """Create a progress bar for a goal."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(pady=3, padx=10, fill="x")

        # Goal name
        ctk.CTkLabel(row, text=goal_name, font=("Arial", 11), width=150, anchor="w").pack(
            side="left", padx=5
        )

        # Progress bar
        percentage = data["percentage"]
        bar_length = min(int(percentage / 2), 40)  # Max 40 chars
        progress_bar = "█" * bar_length + "░" * (40 - bar_length)

        ctk.CTkLabel(
            row,
            text=progress_bar,
            font=("Courier New", 11),
            text_color="#4CAF50" if percentage > 30 else "#FF9800",
            width=250,
            anchor="w",
        ).pack(side="left", padx=5)

        # Time and percentage
        time_str = self.goal_manager.format_duration(data["time_minutes"])
        ctk.CTkLabel(
            row, text=f"{time_str} ({percentage}%)", font=("Arial", 11), width=80, anchor="e"
        ).pack(side="left", padx=5)
