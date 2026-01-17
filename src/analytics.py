
import datetime
from collections import defaultdict

class AnalyticsEngine:
    """Analytics engine for multi-day activity analysis"""
    
    def __init__(self, storage_manager):
        self.storage = storage_manager
    
    def get_daily_summary(self, date):
        """Get summary statistics for a specific day"""
        entries = self.storage.get_entries_for_date(date)
        
        if not entries:
            return {
                "date": date,
                "total_entries": 0,
                "first_entry": None,
                "last_entry": None,
                "hours_tracked": 0
            }
        
        # Parse timestamps
        timestamps = []
        for entry in entries:
            try:
                time_str = entry[0]
                time_obj = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                timestamps.append(time_obj)
            except (ValueError, IndexError):
                continue
        
        if not timestamps:
            return {
                "date": date,
                "total_entries": len(entries),
                "first_entry": None,
                "last_entry": None,
                "hours_tracked": 0
            }
        
        first_time = min(timestamps)
        last_time = max(timestamps)
        
        # Calculate hours tracked (rough estimate)
        first_dt = datetime.datetime.combine(date, first_time)
        last_dt = datetime.datetime.combine(date, last_time)
        hours_tracked = (last_dt - first_dt).total_seconds() / 3600
        
        return {
            "date": date,
            "total_entries": len(entries),
            "first_entry": first_time.strftime("%H:%M"),
            "last_entry": last_time.strftime("%H:%M"),
            "hours_tracked": round(hours_tracked, 1)
        }
    
    def get_week_summary(self, end_date=None):
        """Get summary for last 7 days"""
        if end_date is None:
            end_date = datetime.date.today()
        
        start_date = end_date - datetime.timedelta(days=6)
        
        summaries = []
        current_date = start_date
        
        while current_date <= end_date:
            summary = self.get_daily_summary(current_date)
            summaries.append(summary)
            current_date += datetime.timedelta(days=1)
        
        return summaries
    
    def get_activity_heatmap(self, days=7):
        """Get hour-by-hour activity counts for the last N days"""
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        hour_counts = defaultdict(int)
        
        entries_by_date = self.storage.get_date_range_entries(start_date, end_date)
        
        for date, entries in entries_by_date.items():
            for entry in entries:
                try:
                    time_str = entry[0]
                    hour = int(time_str.split(":")[0])
                    hour_counts[hour] += 1
                except (ValueError, IndexError):
                    continue
        
        return dict(hour_counts)
    
    def get_overall_stats(self, days=7):
        """Get overall statistics for the period"""
        summaries = self.get_week_summary()
        
        total_entries = sum(s["total_entries"] for s in summaries)
        days_with_data = sum(1 for s in summaries if s["total_entries"] > 0)
        
        if days_with_data == 0:
            avg_per_day = 0
        else:
            avg_per_day = total_entries / days_with_data
        
        # Find most productive day
        most_productive = max(summaries, key=lambda x: x["total_entries"])
        
        # Find most active hour
        heatmap = self.get_activity_heatmap(days)
        if heatmap:
            most_active_hour = max(heatmap.items(), key=lambda x: x[1])
        else:
            most_active_hour = (0, 0)
        
        return {
            "total_entries": total_entries,
            "days_with_data": days_with_data,
            "avg_per_day": round(avg_per_day, 1),
            "most_productive_day": most_productive["date"],
            "most_productive_count": most_productive["total_entries"],
            "most_active_hour": most_active_hour[0],
            "most_active_hour_count": most_active_hour[1]
        }
