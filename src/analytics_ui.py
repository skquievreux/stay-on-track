
import datetime
import customtkinter as ctk
from analytics import AnalyticsEngine

class AnalyticsWindow(ctk.CTkToplevel):
    """Multi-day analytics dashboard"""
    
    def __init__(self, storage_manager):
        super().__init__()
        self.storage_manager = storage_manager
        self.analytics = AnalyticsEngine(storage_manager)
        self.days = 7  # Default to last 7 days
        
        self.title("Analytics Dashboard")
        self.geometry("600x700")
        self.attributes("-topmost", True)
        
        # Title
        self.lbl_title = ctk.CTkLabel(
            self, 
            text="📊 Activity Analytics", 
            font=("Arial", 18, "bold")
        )
        self.lbl_title.pack(pady=15)
        
        # Period Selector
        self.period_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.period_frame.pack(pady=10)
        
        ctk.CTkLabel(
            self.period_frame, 
            text="Period:", 
            font=("Arial", 12)
        ).pack(side="left", padx=5)
        
        self.btn_7days = ctk.CTkButton(
            self.period_frame,
            text="Last 7 Days",
            width=100,
            command=lambda: self._change_period(7)
        )
        self.btn_7days.pack(side="left", padx=5)
        
        self.btn_30days = ctk.CTkButton(
            self.period_frame,
            text="Last 30 Days",
            width=100,
            command=lambda: self._change_period(30)
        )
        self.btn_30days.pack(side="left", padx=5)
        
        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=580, height=550)
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
            text=f"📈 Summary (Last {self.days} Days)",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Stats Grid
        stats_text = f"""
Total Entries:        {stats['total_entries']}
Days with Data:       {stats['days_with_data']}
Avg per Day:          {stats['avg_per_day']}
Most Productive:      {stats['most_productive_day']} ({stats['most_productive_count']} entries)
Most Active Hour:     {stats['most_active_hour']:02d}:00 ({stats['most_active_hour_count']} entries)
        """.strip()
        
        ctk.CTkLabel(
            summary_frame,
            text=stats_text,
            font=("Courier New", 12),
            justify="left"
        ).pack(pady=10, padx=20)
        
        # Daily Breakdown Section
        breakdown_frame = ctk.CTkFrame(self.scroll_frame)
        breakdown_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(
            breakdown_frame,
            text="📅 Daily Breakdown",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Show only last 7 days for visualization
        recent_summaries = summaries[-7:] if len(summaries) > 7 else summaries
        
        for summary in reversed(recent_summaries):
            self._create_day_bar(breakdown_frame, summary)
        
        # Activity Heatmap Section
        if heatmap:
            heatmap_frame = ctk.CTkFrame(self.scroll_frame)
            heatmap_frame.pack(pady=10, padx=10, fill="x")
            
            ctk.CTkLabel(
                heatmap_frame,
                text="🕐 Activity by Hour",
                font=("Arial", 14, "bold")
            ).pack(pady=10)
            
            # Show top 5 hours
            sorted_hours = sorted(heatmap.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for hour, count in sorted_hours:
                hour_text = f"{hour:02d}:00 - {hour:02d}:59"
                bar_length = min(count * 3, 40)
                bar = "█" * bar_length
                
                row = ctk.CTkFrame(heatmap_frame, fg_color="transparent")
                row.pack(pady=2, padx=10, fill="x")
                
                ctk.CTkLabel(
                    row,
                    text=f"{hour_text}  {bar}  {count}",
                    font=("Courier New", 11),
                    anchor="w"
                ).pack(side="left")
    
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
            row,
            text=date_label,
            font=("Arial", 11, "bold" if is_today else "normal"),
            width=150,
            anchor="w"
        ).pack(side="left", padx=5)
        
        # Visual bar
        bar_length = min(count * 2, 40)
        bar = "█" * bar_length if count > 0 else "·"
        
        ctk.CTkLabel(
            row,
            text=bar,
            font=("Courier New", 11),
            text_color="#4CAF50" if is_today else "gray",
            anchor="w",
            width=300
        ).pack(side="left", padx=5)
        
        # Count
        ctk.CTkLabel(
            row,
            text=str(count),
            font=("Arial", 11),
            width=40,
            anchor="e"
        ).pack(side="left", padx=5)
