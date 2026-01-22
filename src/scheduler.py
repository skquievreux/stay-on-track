import datetime
import threading
import time


class Scheduler:
    def __init__(self, config_manager, trigger_callback, goal_manager=None):
        self.config_manager = config_manager
        self.trigger_callback = trigger_callback
        self.goal_manager = goal_manager
        self.running = False
        self.next_run_time = None
        self.thread = None
        self.daily_focus_shown_today = False

    def start(self):
        if self.running:
            return
        self.running = True

        # Run in a separate thread to not block GUI
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _get_next_quarter_hour(self):
        now = datetime.datetime.now()
        # Round to next 15 minutes
        minutes = now.minute
        if minutes < 15:
            next_minutes = 15
        elif minutes < 30:
            next_minutes = 30
        elif minutes < 45:
            next_minutes = 45
        else:
            next_minutes = 0

        next_run = now.replace(minute=next_minutes, second=0, microsecond=0)

        if next_minutes == 0:  # Rounded up to next hour
            next_run += datetime.timedelta(hours=1)
            next_run = next_run.replace(minute=0)

        if next_run <= now:  # Should not happen with logic above but safe guard
            next_run += datetime.timedelta(minutes=15)

        return next_run

    def _run_loop(self):
        while self.running:
            self.next_run_time = self._get_next_quarter_hour()
            print(f"Next run scheduled for: {self.next_run_time.strftime('%H:%M:%S')}")

            # Wait loop
            while self.running and datetime.datetime.now() < self.next_run_time:
                time.sleep(1)  # Check every second for stop signal

            if not self.running:
                break

            # Trigger
            self._check_and_trigger()

            # Sleep a bit to avoid double trigger if execution is fast
            time.sleep(2)

    def _check_and_trigger(self):
        current_time_str = datetime.datetime.now().strftime("%H:%M")
        start_time = self.config_manager.get("start_time")
        end_time = self.config_manager.get("end_time")

        if self._is_time_in_range(start_time, end_time):
            print(f"Time {current_time_str} is in range {start_time}-{end_time}. Triggering...")

            # Check if we need to show daily focus first
            needs_daily_focus = self._should_show_daily_focus()

            # Check if we should show end-of-day summary
            should_show_summary = self._should_show_day_summary()

            self.trigger_callback(
                needs_daily_focus=needs_daily_focus, should_show_summary=should_show_summary
            )
        else:
            print(f"Time {current_time_str} is OUT of range {start_time}-{end_time}. Skipping.")

    def _should_show_daily_focus(self):
        """Check if daily focus should be shown before activity popup."""
        if not self.goal_manager:
            return False

        # Check if it's a new day
        today = datetime.date.today()
        if not hasattr(self, "_last_daily_check") or self._last_daily_check != today:
            self._last_daily_check = today
            self.daily_focus_shown_today = False

        # Only show once per day, and only if no daily focus is set
        if not self.daily_focus_shown_today and not self.goal_manager.has_daily_focus_today():
            # Check if it's morning (before 12 PM) - daily focus is primarily for morning
            current_hour = datetime.datetime.now().hour
            if current_hour < 12:  # Before noon
                self.daily_focus_shown_today = True
                return True

        return False

    def _should_show_day_summary(self):
        """Check if end-of-day summary should be shown."""
        if not self.goal_manager:
            return False

        # Check if it's after end time and we haven't shown summary today
        current_time = datetime.datetime.now().time()
        end_time_str = self.config_manager.get("end_time")

        try:
            end_hour, end_minute = map(int, end_time_str.split(":"))
            end_time = datetime.time(end_hour, end_minute)

            # Only show if current time is after end time
            if current_time <= end_time:
                return False

            # Check if we already showed summary today
            today = datetime.date.today()
            if not hasattr(self, "_summary_shown_date") or self._summary_shown_date != today:
                self._summary_shown_date = today
                self._summary_shown_today = False

            if not self._summary_shown_today:
                self._summary_shown_today = True
                return True

        except (ValueError, AttributeError):
            pass

        return False

    def _is_time_in_range(self, start, end):
        now = datetime.datetime.now().time()
        try:
            s_h, s_m = map(int, start.split(":"))
            e_h, e_m = map(int, end.split(":"))
            start_dt = datetime.time(s_h, s_m)
            end_dt = datetime.time(e_h, e_m)

            if start_dt <= end_dt:
                return start_dt <= now <= end_dt
            # Crosses midnight
            return start_dt <= now or now <= end_dt
        except ValueError:
            return False

    def stop(self):
        self.running = False
