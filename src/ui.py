
import customtkinter as ctk

class InputWindow(ctk.CTkToplevel):
    def __init__(self, storage_manager, on_close_callback=None):
        super().__init__()
        self.storage_manager = storage_manager
        self.on_close_callback = on_close_callback
        
        self.title("Stay On Track - Log Activity")
        self.geometry("400x200")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Label
        self.label = ctk.CTkLabel(self, text="What have you worked on?", font=("Arial", 14))
        self.label.pack(pady=10)

        # Entry
        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.submit)
        self.entry.focus_set()

        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.submit_btn = ctk.CTkButton(self.btn_frame, text="Save", command=self.submit)
        self.submit_btn.pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def submit(self, event=None):
        comment = self.entry.get().strip()
        if comment:
            self.storage_manager.save_entry(comment)
        self.on_close()

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, config_manager, on_save_callback=None):
        super().__init__()
        self.config_manager = config_manager
        self.on_save_callback = on_save_callback

        self.title("Settings")
        self.geometry("300x250")
        self.attributes("-topmost", True)

        self._create_widgets()
        self._load_current_values()

    def _create_widgets(self):
        # Time Window
        self.lbl_start = ctk.CTkLabel(self, text="Start Time (HH:MM)")
        self.lbl_start.pack(pady=5)
        self.ent_start = ctk.CTkEntry(self)
        self.ent_start.pack(pady=5)

        self.lbl_end = ctk.CTkLabel(self, text="End Time (HH:MM)")
        self.lbl_end.pack(pady=5)
        self.ent_end = ctk.CTkEntry(self)
        self.ent_end.pack(pady=5)

        # Save Button
        self.btn_save = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.btn_save.pack(pady=20)

    def _load_current_values(self):
        self.ent_start.insert(0, self.config_manager.get("start_time"))
        self.ent_end.insert(0, self.config_manager.get("end_time"))

    def save_settings(self):
        new_config = {
            "start_time": self.ent_start.get().strip(),
            "end_time": self.ent_end.get().strip()
        }
        self.config_manager.save_config(new_config)
        
        if self.on_save_callback:
            self.on_save_callback()
        
        self.destroy()

class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, storage_manager):
        super().__init__()
        self.storage_manager = storage_manager
        self.title("Today's Activity")
        self.geometry("400x500")
        self.attributes("-topmost", True)
        
        # Title
        self.lbl_title = ctk.CTkLabel(self, text="Activity Log", font=("Arial", 16, "bold"))
        self.lbl_title.pack(pady=10)

        # Scrollable Frame for items
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=380, height=400)
        self.scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self._load_entries()

    def _load_entries(self):
        entries = self.storage_manager.get_today_entries()
        
        if not entries:
            lbl = ctk.CTkLabel(self.scroll_frame, text="No entries for today.")
            lbl.pack(pady=10)
            return

        # Reverse order to see latest first
        for entry in reversed(entries):
            # entry structure: [Timestamp, Comment]
            if len(entry) < 2: continue
            
            timestamp = entry[0]
            comment = entry[1]
            
            # Row Frame
            row_frame = ctk.CTkFrame(self.scroll_frame)
            row_frame.pack(pady=2, padx=5, fill="x")
            
            lbl_time = ctk.CTkLabel(row_frame, text=timestamp, text_color="gray", width=60)
            lbl_time.pack(side="left", padx=5)
            
            lbl_comment = ctk.CTkLabel(row_frame, text=comment, anchor="w", wraplength=250)
            lbl_comment.pack(side="left", padx=5, fill="x", expand=True)
