"""SQLite-based storage manager for Stay-On-Track application."""

import csv
import datetime
import os
import sqlite3
from pathlib import Path


class StorageManager:
    """Manages activity entries using SQLite database."""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "stayontrack.db")
        # Keep output_dir for backwards compatibility (used by HistoryWindow)
        self.output_dir = data_dir
        self._ensure_data_dir()
        self._init_db()

    def _ensure_data_dir(self):
        """Ensure the data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def _init_db(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create entries table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    activity TEXT NOT NULL,
                    effectiveness TEXT CHECK(effectiveness IN ('good', 'bad') OR effectiveness IS NULL)
                )
            """
            )

            # Create index for faster date-based queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_entries_timestamp ON entries(timestamp)
            """
            )

            # Create migrations table to track CSV import
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migrated_at DATETIME NOT NULL,
                    entries_count INTEGER NOT NULL,
                    source TEXT
                )
            """
            )

            conn.commit()

    def _get_connection(self):
        """Get a database connection with row factory for dict-like access."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # =========================================================================
    # Core Operations
    # =========================================================================

    def save_entry(self, activity, effectiveness=None):
        """
        Save a new activity entry.

        Args:
            activity: The activity description text
            effectiveness: Optional effectiveness rating ('good' or 'bad')
        """
        timestamp = datetime.datetime.now()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO entries (timestamp, activity, effectiveness) VALUES (?, ?, ?)",
                (timestamp.isoformat(), activity, effectiveness),
            )
            conn.commit()

        print(f"Saved: {timestamp.strftime('%H:%M:%S')} - {activity}")

    def get_last_entry_time(self):
        """
        Get the timestamp of the most recent entry.

        Returns:
            datetime object or None if no entries exist
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp FROM entries ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()

            if row:
                return datetime.datetime.fromisoformat(row["timestamp"])
            return None

    def get_recent_entries(self, limit=2):
        """
        Get the most recent entries.

        Args:
            limit: Number of entries to return (default: 2)

        Returns:
            List of entry dicts with keys: id, timestamp, activity, effectiveness
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, activity, effectiveness FROM entries "
                "ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()

            return [
                {
                    "id": row["id"],
                    "timestamp": datetime.datetime.fromisoformat(row["timestamp"]),
                    "activity": row["activity"],
                    "effectiveness": row["effectiveness"],
                }
                for row in rows
            ]

    # =========================================================================
    # Date-based Queries
    # =========================================================================

    def get_today_entries(self):
        """Get all entries for today."""
        return self.get_entries_for_date(datetime.date.today())

    def get_entries_for_date(self, date):
        """
        Get all entries for a specific date.

        Args:
            date: A datetime.date object

        Returns:
            List of entry dicts with keys: id, timestamp, activity, effectiveness
        """
        start_of_day = datetime.datetime.combine(date, datetime.time.min)
        end_of_day = datetime.datetime.combine(date, datetime.time.max)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, activity, effectiveness FROM entries "
                "WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp ASC",
                (start_of_day.isoformat(), end_of_day.isoformat()),
            )
            rows = cursor.fetchall()

            return [
                {
                    "id": row["id"],
                    "timestamp": datetime.datetime.fromisoformat(row["timestamp"]),
                    "activity": row["activity"],
                    "effectiveness": row["effectiveness"],
                }
                for row in rows
            ]

    def get_date_range_entries(self, start_date, end_date):
        """
        Get entries for a date range, grouped by date.

        Args:
            start_date: Start date (datetime.date)
            end_date: End date (datetime.date)

        Returns:
            Dict mapping date to list of entry dicts
        """
        entries_by_date = {}
        current_date = start_date

        while current_date <= end_date:
            entries = self.get_entries_for_date(current_date)
            if entries:
                entries_by_date[current_date] = entries
            current_date += datetime.timedelta(days=1)

        return entries_by_date

    def get_all_log_files(self):
        """
        Get list of all dates with entries.

        Returns:
            List of dicts with 'file' (db path) and 'date' keys, sorted by date descending
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT DATE(timestamp) as entry_date FROM entries ORDER BY entry_date DESC"
            )
            rows = cursor.fetchall()

            return [
                {
                    "file": self.db_path,
                    "date": datetime.datetime.strptime(row["entry_date"], "%Y-%m-%d").date(),
                }
                for row in rows
                if row["entry_date"]
            ]

    # =========================================================================
    # CSV Migration
    # =========================================================================

    def needs_migration(self):
        """
        Check if CSV migration is needed.

        Returns:
            True if CSV files exist and haven't been migrated yet
        """
        # Check if migration was already performed
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM migrations WHERE source = 'csv'")
            row = cursor.fetchone()
            if row["count"] > 0:
                return False

        # Check if CSV files exist
        csv_files = list(Path(self.data_dir).glob("logs_*.csv"))
        return len(csv_files) > 0

    def migrate_from_csv(self):
        """
        Migrate all existing CSV files to SQLite database.

        Returns:
            Number of entries migrated
        """
        csv_files = list(Path(self.data_dir).glob("logs_*.csv"))
        migrated_count = 0
        errors = []

        for csv_file in csv_files:
            try:
                # Extract date from filename: logs_2026-01-17.csv
                date_str = csv_file.stem.replace("logs_", "")
                file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

                with open(csv_file, encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader, None)  # Skip header row

                    for row in reader:
                        if len(row) >= 2:
                            time_str = row[0]  # "14:30:00"
                            activity = row[1]

                            try:
                                # Combine date + time
                                time_obj = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                                timestamp = datetime.datetime.combine(file_date, time_obj)

                                # Insert into database
                                with sqlite3.connect(self.db_path) as conn:
                                    cursor = conn.cursor()
                                    cursor.execute(
                                        "INSERT INTO entries (timestamp, activity, effectiveness) "
                                        "VALUES (?, ?, ?)",
                                        (timestamp.isoformat(), activity, None),
                                    )
                                    conn.commit()

                                migrated_count += 1
                            except ValueError as e:
                                errors.append(f"Error parsing {csv_file.name}, row {row}: {e}")

            except (FileNotFoundError, csv.Error) as e:
                errors.append(f"Error reading {csv_file}: {e}")

        # Record migration
        if migrated_count > 0:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO migrations (migrated_at, entries_count, source) VALUES (?, ?, ?)",
                    (datetime.datetime.now().isoformat(), migrated_count, "csv"),
                )
                conn.commit()

        # Log any errors
        for error in errors:
            print(f"Migration warning: {error}")

        print(
            f"Migration complete: {migrated_count} entries imported from {len(csv_files)} CSV files"
        )
        return migrated_count
