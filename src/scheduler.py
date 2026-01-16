
import time
import datetime
import threading

class Scheduler:
    def __init__(self, config_manager, trigger_callback):
        self.config_manager = config_manager
        self.trigger_callback = trigger_callback
        self.running = False
        self.next_run_time = None

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
        
        if next_minutes == 0: # Rounded up to next hour
            next_run += datetime.timedelta(hours=1)
            next_run = next_run.replace(minute=0)
            
        if next_run <= now: # Should not happen with logic above but safe guard
            next_run += datetime.timedelta(minutes=15)
            
        return next_run

    def _run_loop(self):
        while self.running:
            self.next_run_time = self._get_next_quarter_hour()
            print(f"Next run scheduled for: {self.next_run_time.strftime('%H:%M:%S')}")
            
            # Wait loop
            while self.running and datetime.datetime.now() < self.next_run_time:
                time.sleep(1) # Check every second for stop signal
            
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
            self.trigger_callback()
        else:
            print(f"Time {current_time_str} is OUT of range {start_time}-{end_time}. Skipping.")

    def _is_time_in_range(self, start, end):
        now = datetime.datetime.now().time()
        try:
            s_h, s_m = map(int, start.split(":"))
            e_h, e_m = map(int, end.split(":"))
            start_dt = datetime.time(s_h, s_m)
            end_dt = datetime.time(e_h, e_m)
            
            if start_dt <= end_dt:
                return start_dt <= now <= end_dt
            else: # Crosses midnight
                return start_dt <= now or now <= end_dt
        except ValueError:
            return False

    def stop(self):
        self.running = False
