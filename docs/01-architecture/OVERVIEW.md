# Architecture Overview

## Core Components

### 1. Main Application (`main.py`)
- Entry point.
- Initializes specific managers.
- Handles System Tray integration (`pystray`).
- Manages the thread loop for the tray icon.

### 2. Scheduler (`scheduler.py`)
- **Responsibility**: Triggers events at specific times.
- **Logic**: Aligns to quarter hours (:00, :15, :30, :45).
- **Thread**: Runs in a separate daemon thread to avoid blocking the UI.

### 3. UI Layer (`ui.py`)
- Built with `customtkinter`.
- **InputWindow**: Popup for entering data.
- **SettingsWindow**: Configuration of start/end times.
- **HistoryWindow**: Read-only view of today's CSV data.

### 4. Data Layer (`storage.py` & `config.py`)
- **Storage**: Appends to `logs_YYYY-MM-DD.csv`.
- **Config**: JSON-based persistent settings.

## Data Flow
1. Scheduler wakes up -> Checks Time Window.
2. If valid -> Triggers Callback (Main Thread).
3. Callback -> Shows InputWindow.
4. User Saves -> StorageManager writes CSV.
