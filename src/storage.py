
import csv
import datetime
import os

class StorageManager:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def _get_daily_filename(self):
        today = datetime.date.today()
        return os.path.join(self.output_dir, f"logs_{today.strftime('%Y-%m-%d')}.csv")

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
        filename = self._get_daily_filename()
        if not os.path.exists(filename):
            return []

        entries = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header
                for row in reader:
                    if len(row) >= 2:
                        entries.append(row)
        except (FileNotFoundError, csv.Error) as e:
            print(f"Error reading log: {e}")
            return []

        return entries
