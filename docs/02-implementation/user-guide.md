# User Guide

## Getting Started

### First Launch

After installing Stay-On-Track, the application will:
1. Start automatically and appear in your system tray
2. Create a data folder at `C:\Users\YourName\Documents\StayOnTrack`
3. Show the settings window to configure your active hours

### System Tray Icon

Look for the 📊 icon in your Windows system tray (bottom-right corner).

**Right-click the icon** to access:
- **Log Activity** - Manually log an activity
- **Show History** - View today's entries
- **Analytics (Multi-Day)** - Open analytics dashboard
- **Settings** - Configure active time window
- **Exit** - Close the application

## Daily Usage

### Automatic Reminders

Every 15 minutes (at :00, :15, :30, :45), Stay-On-Track will:
1. Play a sound notification 🔔
2. Show an input dialog
3. Wait for you to describe your current activity

**Example entries:**
```
Meeting mit Team
Code schreiben
Pause / Kaffee
Dokumentation lesen
```

### Manual Logging

You can also log activities manually:
1. Right-click the tray icon
2. Select "Log Activity"
3. Enter your activity description
4. Click "Save"

## Viewing Your Data

### History Window

**Access:** Right-click tray icon → "Show History"

![History Window](../screenshots/history-window.png)

**Features:**
- View all entries for a specific day
- Navigate between dates with **◀ Prev** and **Next ▶** buttons
- Jump to today with **Today** button
- Open data folder with **📁 Open Folder** button

### Analytics Dashboard

**Access:** Right-click tray icon → "Analytics (Multi-Day)"

![Analytics Dashboard](../screenshots/analytics-dashboard.png)

**Time Periods:**
- Last 7 days
- Last 30 days

**Metrics:**
- Total entries
- Average entries per day
- Most productive day
- Most active hour
- Category breakdown
- Daily activity chart
- Hourly heatmap

## Configuration

### Settings Window

**Access:** Right-click tray icon → "Settings"

**Options:**
- **Start Time** - When to begin reminders (e.g., `09:00`)
- **End Time** - When to stop reminders (e.g., `18:00`)

**Example:**
```
Start Time: 09:00
End Time: 18:00
```
→ Reminders will only appear between 9 AM and 6 PM

### Config File

Advanced users can edit the configuration file directly:

**Location:** `C:\Users\YourName\Documents\StayOnTrack\config.json`

```json
{
  "start_time": "09:00",
  "end_time": "18:00",
  "output_dir": "C:/Users/YourName/Documents/StayOnTrack"
}
```

## Data Management

### CSV Files

Your activities are stored in daily CSV files:

```
C:\Users\YourName\Documents\StayOnTrack\
├── logs_2026-01-17.csv
├── logs_2026-01-16.csv
├── logs_2026-01-15.csv
└── ...
```

**Format:**
```csv
Timestamp,Activity
09:00:13,Tagebuch geschrieben
09:15:42,Jobsuche Freelancermap
09:30:11,Meeting mit Team
```

### Backup

To backup your data:
1. Open the data folder (📁 button in History window)
2. Copy all `.csv` files to a backup location

### Export

CSV files can be opened with:
- Microsoft Excel
- Google Sheets
- LibreOffice Calc
- Any text editor

## Tips & Tricks

### Effective Activity Descriptions

**✅ Good:**
- "Meeting mit Team über Feature X"
- "Code Review PR #123"
- "Dokumentation schreiben"
- "Pause / Mittagessen"

**❌ Less useful:**
- "Arbeit"
- "Verschiedenes"
- "..."

### Keyboard Shortcuts

- **Enter** - Save activity
- **Escape** - Cancel (skips this entry)

### Auto-Start

Stay-On-Track starts automatically with Windows. To disable:
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to "Startup" tab
3. Find "Stay On Track"
4. Right-click → Disable

---

**Next:** [Analytics & Categories](analytics.md) | [Troubleshooting](../03-operations/troubleshooting.md)
