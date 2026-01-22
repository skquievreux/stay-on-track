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
                    effectiveness TEXT CHECK(effectiveness IN ('good', 'bad') OR effectiveness IS NULL),
                    goal_id INTEGER REFERENCES goals(id)
                )
            """

            # Create index for faster date-based queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_entries_timestamp ON entries(timestamp)
            """

            # Create goals table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parent_id INTEGER REFERENCES goals(id),
                    is_active BOOLEAN DEFAULT 1,
                    is_archived BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """

            # Create daily_focus table (daily goal selection)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_focus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    goal_id INTEGER REFERENCES goals(id),
                    adhoc_name TEXT,
                    priority INTEGER CHECK(priority BETWEEN 1 AND 3),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, priority)
                )
            """

            # Create streaks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS streaks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    length INTEGER DEFAULT 1
                )
            """

            # Create achievements table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    achievement_key TEXT NOT NULL UNIQUE,
                    unlocked_at DATETIME NOT NULL,
                    notified BOOLEAN DEFAULT 0
                )
            """

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

        print(f"Migration complete: {migrated_count} entries imported from {len(csv_files)} CSV files")
        return migrated_count

    # =========================================================================
    # Goal Management
    # =========================================================================

    def create_goal(self, name, parent_id=None):
        """Create a new goal."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO goals (name, parent_id) VALUES (?, ?)",
                (name, parent_id),
            )
            goal_id = cursor.lastrowid
            conn.commit()
            return goal_id

    def get_active_goals(self):
        """Get all active goals (not archived)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, parent_id FROM goals WHERE is_active = 1 AND is_archived = 0 ORDER BY name"
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "parent_id": row["parent_id"],
                }
                for row in rows
            ]

    def get_subgoals(self, parent_id):
        """Get subgoals for a parent goal."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name FROM goals WHERE parent_id = ? AND is_active = 1 AND is_archived = 0 ORDER BY name",
                (parent_id,),
            )
            rows = cursor.fetchall()
            return [
                {"id": row["id"], "name": row["name"]}
                for row in rows
            ]

    def archive_goal(self, goal_id):
        """Archive a goal (soft delete)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE goals SET is_archived = 1 WHERE id = ?",
                (goal_id,),
            )
            conn.commit()

    def restore_goal(self, goal_id):
        """Restore an archived goal."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE goals SET is_archived = 0 WHERE id = ?",
                (goal_id,),
            )
            conn.commit()

    def update_goal_name(self, goal_id, new_name):
        """Update a goal's name."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE goals SET name = ? WHERE id = ?",
                (new_name, goal_id),
            )
            conn.commit()

    def has_any_goals(self):
        """Check if any goals exist (for first-time setup)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM goals WHERE is_archived = 0")
            row = cursor.fetchone()
            return row["count"] > 0

    # =========================================================================
    # Daily Focus Management
    # =========================================================================

    def set_daily_focus(self, date, goals):
        """
        Set daily focus goals for a date.
        goals: list of dicts with 'goal_id' (optional) and 'adhoc_name' (optional)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Clear existing daily focus for this date
            cursor.execute("DELETE FROM daily_focus WHERE date = ?", (date.isoformat(),))

            # Insert new daily focus
            for i, goal in enumerate(goals[:3]):  # Max 3
                cursor.execute(
                    "INSERT INTO daily_focus (date, goal_id, adhoc_name, priority) VALUES (?, ?, ?, ?)",
                    (date.isoformat(), goal.get("goal_id"), goal.get("adhoc_name"), i + 1),
                )
            conn.commit()

    def get_daily_focus(self, date):
        """Get daily focus goals for a date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT df.id, df.goal_id, df.adhoc_name, df.priority, g.name as goal_name
                FROM daily_focus df
                LEFT JOIN goals g ON df.goal_id = g.id
                WHERE df.date = ?
                ORDER BY df.priority
                """,
                (date.isoformat(),),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "goal_id": row["goal_id"],
                    "goal_name": row["goal_name"],
                    "adhoc_name": row["adhoc_name"],
                    "priority": row["priority"],
                }
                for row in rows
            ]

    def has_daily_focus_today(self):
        """Check if daily focus is set for today."""
        today = datetime.date.today()
        daily_focus = self.get_daily_focus(today)
        return len(daily_focus) > 0

    def get_recent_adhoc_goals(self, days=7):
        """Get adhoc goals from the last N days as suggestions."""
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT DISTINCT adhoc_name
                FROM daily_focus
                WHERE date BETWEEN ? AND ? AND adhoc_name IS NOT NULL
                ORDER BY date DESC
                """,
                (start_date.isoformat(), end_date.isoformat()),
            )
            rows = cursor.fetchall()
            return [row["adhoc_name"] for row in rows if row["adhoc_name"]]

    def cleanup_old_adhoc_goals(self, days=7):
        """Remove adhoc goals older than N days."""
        cutoff_date = datetime.date.today() - datetime.timedelta(days=days)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM daily_focus WHERE date < ? AND adhoc_name IS NOT NULL",
                (cutoff_date.isoformat(),),
            )
            conn.commit()

    # =========================================================================
    # Activity-Goal Linking
    # =========================================================================

    def link_activity_to_goal(self, entry_id, goal_id):
        """Link an activity entry to a goal."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE entries SET goal_id = ? WHERE id = ?",
                (goal_id, entry_id),
            )
            conn.commit()

    def get_activities_for_goal(self, goal_id, date=None):
        """Get activities linked to a goal, optionally filtered by date."""
        query = """
            SELECT e.id, e.timestamp, e.activity, e.effectiveness
            FROM entries e
            WHERE e.goal_id = ?
        """
        params = [goal_id]

        if date:
            start_of_day = datetime.datetime.combine(date, datetime.time.min)
            end_of_day = datetime.datetime.combine(date, datetime.time.max)
            query += " AND e.timestamp BETWEEN ? AND ?"
            params.extend([start_of_day.isoformat(), end_of_day.isoformat()])

        query += " ORDER BY e.timestamp DESC"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
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

    def get_goal_progress(self, goal_id, start_date, end_date):
        """Get progress data for a goal over a date range."""
        activities = []
        current_date = start_date
        while current_date <= end_date:
            day_activities = self.get_activities_for_goal(goal_id, current_date)
            activities.extend(day_activities)
            current_date += datetime.timedelta(days=1)

        # Calculate time-based progress (15 min per activity)
        total_minutes = len(activities) * 15
        good_count = sum(1 for a in activities if a["effectiveness"] == "good")
        bad_count = sum(1 for a in activities if a["effectiveness"] == "bad")

        return {
            "goal_id": goal_id,
            "activities": len(activities),
            "time_minutes": total_minutes,
            "good_count": good_count,
            "bad_count": bad_count,
        }

    # =========================================================================
    # Streaks & Achievements
    # =========================================================================

    def update_streak(self, date):
        """Update streak based on goal-related activities on a date."""
        # Check if there were any goal-related activities on this date
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) as count
                FROM entries
                WHERE DATE(timestamp) = ? AND goal_id IS NOT NULL
                """,
                (date.isoformat(),),
            )
            row = cursor.fetchone()
            has_goal_activity = row["count"] > 0

        if not has_goal_activity:
            # End current streak if it exists
            self._end_current_streak()
            return

        # Check if there's an active streak
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, start_date, length FROM streaks WHERE end_date IS NULL ORDER BY id DESC LIMIT 1"
            )
            active_streak = cursor.fetchone()

        if active_streak:
            # Check if this continues the streak (consecutive days)
            last_streak_date = datetime.datetime.fromisoformat(active_streak["start_date"]).date() + datetime.timedelta(days=active_streak["length"] - 1)
            if last_streak_date == date - datetime.timedelta(days=1):
                # Continue streak
                new_length = active_streak["length"] + 1
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE streaks SET length = ? WHERE id = ?",
                        (new_length, active_streak["id"]),
                    )
                    conn.commit()
            else:
                # Start new streak
                self._end_current_streak()
                self._start_new_streak(date)
        else:
            # Start new streak
            self._start_new_streak(date)

    def _start_new_streak(self, date):
        """Start a new streak."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO streaks (start_date, length) VALUES (?, 1)",
                (date.isoformat(),),
            )
            conn.commit()

    def _end_current_streak(self):
        """End the current active streak."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, start_date, length FROM streaks WHERE end_date IS NULL ORDER BY id DESC LIMIT 1"
            )
            active_streak = cursor.fetchone()

        if active_streak:
            end_date = datetime.datetime.fromisoformat(active_streak["start_date"]).date() + datetime.timedelta(days=active_streak["length"] - 1)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE streaks SET end_date = ? WHERE id = ?",
                    (end_date.isoformat(), active_streak["id"]),
                )
                conn.commit()

    def get_current_streak(self):
        """Get the current active streak length."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT length FROM streaks WHERE end_date IS NULL ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            return row["length"] if row else 0

    def get_longest_streak(self):
        """Get the longest streak ever achieved."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(length) as max_length FROM streaks")
            row = cursor.fetchone()
            return row["max_length"] or 0

    def unlock_achievement(self, achievement_key):
        """Unlock an achievement if not already unlocked."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM achievements WHERE achievement_key = ?",
                (achievement_key,),
            )
            if cursor.fetchone():
                return False  # Already unlocked

        # Unlock achievement
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO achievements (achievement_key, unlocked_at) VALUES (?, ?)",
                (achievement_key, datetime.datetime.now().isoformat()),
            )
            conn.commit()
        return True

    def get_unlocked_achievements(self):
        """Get all unlocked achievements."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT achievement_key, unlocked_at FROM achievements ORDER BY unlocked_at DESC"
            )
            rows = cursor.fetchall()
            return [
                {
                    "key": row["achievement_key"],
                    "unlocked_at": datetime.datetime.fromisoformat(row["unlocked_at"]),
                }
                for row in rows
            ]

    def get_pending_achievement_notifications(self):
        """Get achievements that haven't been notified yet."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, achievement_key FROM achievements WHERE notified = 0 ORDER BY unlocked_at DESC"
            )
            rows = cursor.fetchall()
            return [
                {"id": row["id"], "key": row["achievement_key"]}
                for row in rows
            ]

    def mark_achievement_notified(self, achievement_id):
        """Mark an achievement as notified."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE achievements SET notified = 1 WHERE id = ?",
                (achievement_id,),
            )
            conn.commit()
