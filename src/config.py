
import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "start_time": "09:00",
    "end_time": "17:00",
    "output_dir": str(Path.home() / "Documents" / "StayOnTrack"),
}

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.ensure_output_dir()

    def load_config(self):
        if not os.path.exists(self.config_file):
            return DEFAULT_CONFIG.copy()
        try:
            with open(self.config_file, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except json.JSONDecodeError:
             return DEFAULT_CONFIG.copy()

    def save_config(self, new_config):
        self.config.update(new_config)
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
        self.ensure_output_dir()

    def get(self, key):
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def ensure_output_dir(self):
        path = self.get("output_dir")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
