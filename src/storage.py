
import csv
import datetime
import os
from pathlib import Path

class StorageManager:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def _get_daily_filename(self, date=None):
        if date is None:
            date = datetime.date.today()
        return os.path.join(self.output_dir, f"logs_{date.strftime('%Y-%m-%d')}.csv")

    def save_entry(self, comment):
        filename = self._get_daily_filename()
        file_exists = os.path.exists(filename)

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        with open(filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Activity"])
            writer.writerow([timestamp, comment])

        print(f"Saved: {timestamp} - {comment}")

    def get_today_entries(self):
        """Get entries for today"""
        return self.get_entries_for_date(datetime.date.today())

    def get_entries_for_date(self, date):
        """Get entries for a specific date"""
        filename = self._get_daily_filename(date)
        if not os.path.exists(filename):
            return []

        entries = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        entries.append(row)
        except (FileNotFoundError, csv.Error) as e:
            print(f"Error reading log: {e}")
            return []

        return entries

    def get_all_log_files(self):
        """Get list of all log files with their dates"""
        if not os.path.exists(self.output_dir):
            return []

        log_files = []
        for file in Path(self.output_dir).glob("logs_*.csv"):
            # Extract date from filename: logs_2026-01-17.csv
            try:
                date_str = file.stem.replace("logs_", "")
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                log_files.append({"file": str(file), "date": date})
            except ValueError:
                continue

        # Sort by date descending (newest first)
        log_files.sort(key=lambda x: x["date"], reverse=True)
        return log_files

    def get_date_range_entries(self, start_date, end_date):
        """Get entries for a date range"""
        entries_by_date = {}
        current_date = start_date

        while current_date <= end_date:
            entries = self.get_entries_for_date(current_date)
            if entries:
                entries_by_date[current_date] = entries
            current_date += datetime.timedelta(days=1)

        return entries_by_date
