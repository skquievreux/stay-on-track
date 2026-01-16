# Stay On Track

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

**Stay On Track** is a minimalist productivity tool designed to help you maintain focus and track your workday with zero friction. It sits quietly in your system tray and gently prompts you every 15 minutes to log your current activity.

## ✨ Features

- ** unobtrusive Reminders**: Popups appear at quarter-hour intervals (:00, :15, :30, :45).
- **📝 Effortless Logging**: Just type and hit Enter. No complex forms.
- **📊 Daily History**: View a chronological log of today's activities directly within the app.
- **⚙️ Customizable**: Set your preferred workday start and end times.
- **🔒 Privacy First**: All data is stored locally in `Documents/StayOnTrack`. No cloud, no tracking.
- **🚀 Auto-Start**: Simply check the option during installation to run at startup.

## 📥 Installation

### Download
Download the latest Windows Installer (`StayOnTrack_Setup.exe`) from the [Releases](https://github.com/skquievreux/stay-on-track/releases) page.

### Setup
1.  Run the installer.
2.  Follow the prompts.
3.  (Optional) Select "Run at Windows startup" for the best experience.
4.  Launch "Stay On Track" from your Desktop or Start Menu.

## 🛠️ Usage

1.  **System Tray**: Look for the black/green square icon in your system tray (near the clock).
2.  **Log Activity**: When prompted, type what you are working on.
3.  **Right-Click Menu**: access additional features:
    -   **Next Reminder**: See when the next prompt is due.
    -   **Log Activity**: Manually trigger the popup.
    -   **Show History**: Review today's logs.
    -   **Settings**: Adjust start/end times.

## 📂 Data Storage

Your activity logs and configuration are strictly local:
-   **Logs**: `C:\Users\<YOU>\Documents\StayOnTrack\YYYY-MM-DD.csv`
-   **Config**: `C:\Users\<YOU>\Documents\StayOnTrack\config.json`

## 💻 Development

Want to contribute or build from source?

### Prerequisites
-   Python 3.10+
-   Git

### Setup

```bash
git clone https://github.com/skquievreux/stay-on-track.git
cd stay-on-track
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### Run Locally

```bash
python src/main.py
```

### Build Installer
We use PyInstaller and Inno Setup.

1.  **Build EXE**:
    ```bash
    pyinstaller build.spec
    ```
2.  **Create Setup**:
    Compile `setup_script.iss` using Inno Setup Compiler.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
