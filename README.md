# Stay-On-Track

**Simple productivity tracker that helps you stay focused and analyze your work patterns.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🎯 Features

### Core Functionality
- ⏰ **15-Minute Reminders** - Aligned to quarter-hour intervals (:00, :15, :30, :45)
- 💾 **Daily CSV Logs** - Automatic storage in `Documents/StayOnTrack`
- 🔔 **Sound Notifications** - Audio alert when reminder appears
- ⚙️ **Configurable Time Window** - Set active hours for reminders
- 🚀 **Auto-Start** - Runs automatically with Windows

### Analytics & Insights (NEW v1.1.0)
- 📊 **Multi-Day Analytics** - View statistics for last 7 or 30 days
- 📅 **Date Navigation** - Browse history with Prev/Next/Today buttons
- 📁 **Folder Access** - Quick link to open data directory
- 🎨 **Activity Clustering** - Automatic categorization into 9 categories
- 🤖 **Auto-Learning** - Discovers new patterns from your activities
- 📈 **Category Breakdown** - Visual analytics with color-coded bars

## 📦 Installation

### Quick Start

1. **Download the installer** from [Releases](https://github.com/YOUR_USERNAME/Stay-On-Track/releases)
2. **Run `StayOnTrackSetup.exe`**
3. **Launch from Start Menu** or Desktop shortcut

### Manual Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Stay-On-Track.git
cd Stay-On-Track

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

## 🚀 Usage

### System Tray Menu

Right-click the tray icon to access:

- **Log Activity** - Manually log an activity
- **Show History** - View and navigate through past entries
- **Analytics (Multi-Day)** - Comprehensive analytics dashboard
- **Settings** - Configure active time window
- **Exit** - Close application

### History Window

![History Window](docs/screenshots/history-window.png)

- **◀ Prev / Next ▶** - Navigate between dates
- **Today** - Jump to current day
- **📁 Open Folder** - Access CSV files directly

### Analytics Dashboard

![Analytics Dashboard](docs/screenshots/analytics-dashboard.png)

**Summary Statistics:**
- Total entries across period
- Average entries per day
- Most productive day
- Most active hour

**Category Breakdown:**
- 🍽️ Essen - Meals and breaks
- 💼 Jobsuche - Job search activities
- 💬 Meetings - Discussions and calls
- 🛠️ Entwicklung - Development work
- 📝 Dokumentation - Documentation tasks
- 🤖 KI/Automation - AI tools and automation
- 📚 Lernen - Learning and training
- ✍️ Schreiben - Writing tasks
- 🔍 Recherche - Research activities

**Daily Breakdown:**
- Visual bars showing activity per day
- Color-coded for easy scanning

**Activity Heatmap:**
- Top 5 most active hours
- Identify your peak productivity times

## 🎨 Activity Clustering

### How It Works

**Automatic Categorization:**
```python
"Frühstück" → 🍽️ Essen
"Meeting mit Team" → 💬 Meetings
"Code schreiben" → 🛠️ Entwicklung
"Claude fragen" → 🤖 KI/Automation
```

**Auto-Learning:**
- Analyzes uncategorized entries every 7 days
- Suggests categories for frequent phrases
- Learns from your feedback
- Stores custom keywords in `learned_keywords.json`

### Example Analysis

**Your Activities:**
```
09:30  Jobsuche Freelancermap
10:00  Langdock einarbeitung
10:30  Diskussion mit der KI
11:11  Frühstück
12:12  Erklärung von Timetracker
```

**Category Breakdown:**
- 🤖 KI/Automation: 22%
- 📚 Lernen: 17%
- 💼 Jobsuche: 17%
- 📝 Dokumentation: 17%
- 💬 Meetings: 17%
- 🍽️ Essen: 11%

## 📊 Data Storage

### File Structure

```
C:\Users\YourName\Documents\StayOnTrack\
├── logs_2026-01-17.csv
├── logs_2026-01-16.csv
├── logs_2026-01-15.csv
├── learned_keywords.json
└── config.json
```

### CSV Format

```csv
Timestamp,Activity
09:13:43,Tagebuch geschrieben
09:30:13,Jobsuche Freelancermap
10:00:11,Langdock einarbeitung
```

### Learned Keywords

```json
{
  "learned_keywords": {
    "💬 Meetings": {
      "keywords": ["standup", "daily"],
      "usage_count": 15
    }
  }
}
```

## ⚙️ Configuration

### Settings Window

- **Start Time** - Begin reminders (e.g., `09:00`)
- **End Time** - Stop reminders (e.g., `18:00`)

### Config File

Located at: `C:\Users\YourName\Documents\StayOnTrack\config.json`

```json
{
  "start_time": "09:00",
  "end_time": "18:00",
  "output_dir": "C:/Users/YourName/Documents/StayOnTrack"
}
```

## 🛠️ Development

### Project Structure

```
Stay-On-Track/
├── src/
│   ├── main.py              # Application entry point
│   ├── ui.py                # UI components
│   ├── storage.py           # Data persistence
│   ├── scheduler.py         # Reminder scheduling
│   ├── analytics.py         # Analytics engine
│   ├── analytics_ui.py      # Analytics dashboard
│   ├── category_engine.py   # Activity categorization
│   └── config.py            # Configuration management
├── build.spec               # PyInstaller configuration
├── setup_script.iss         # Inno Setup installer script
└── requirements.txt         # Python dependencies
```

### Building from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
pyinstaller build.spec

# Create installer (requires Inno Setup)
iscc setup_script.iss
```

### Running Tests

```bash
# Unit tests (when implemented)
pytest tests/

# Manual testing
python src/main.py
```

## 📝 Changelog

### v1.1.0 (2026-01-17)

**New Features:**
- ✨ Multi-day analytics dashboard
- ✨ Activity clustering with 9 categories
- ✨ Auto-learning system for pattern discovery
- ✨ Date navigation in history window
- ✨ Folder access button
- ✨ Category breakdown visualization

**Improvements:**
- 📊 Enhanced analytics with color-coded bars
- 🎨 Improved UI with larger windows
- 💾 Learned keywords persistence

### v1.0.0 (2026-01-15)

**Initial Release:**
- ⏰ 15-minute interval reminders
- 💾 Daily CSV logging
- 🔔 Sound notifications
- ⚙️ Configurable time window
- 🚀 Windows auto-start

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Icons from [Lucide](https://lucide.dev/)
- Inspired by productivity tracking best practices

---

**Made with ❤️ for better productivity tracking**
