
import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "start_time": "09:00",
    "end_time": "17:00",
    "output_dir": str(Path.home() / "Documents" / "StayOnTrack"),
}

class ConfigManager:
    def __init__(self, config_filename="config.json"):
        # Store config in the same place as the output_dir for simplicity and persistence
        self.config_dir = Path.home() / "Documents" / "StayOnTrack"
        self.config_file = self.config_dir / config_filename
        self.ensure_config_dir()
        self.config = self.load_config()
        self.ensure_output_dir()

    def ensure_config_dir(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self):
        if not self.config_file.exists():
            return DEFAULT_CONFIG.copy()
        try:
            with open(self.config_file, "r") as f:
                loaded = json.load(f)
                # Merge with default to ensure all keys exist
                return {**DEFAULT_CONFIG, **loaded}
        except json.JSONDecodeError:
             return DEFAULT_CONFIG.copy()

    def save_config(self, new_config):
        self.config.update(new_config)
        self.ensure_config_dir()
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
        self.ensure_output_dir()

    def get(self, key):
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def ensure_output_dir(self):
        path = self.get("output_dir")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
