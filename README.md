
# Stay On Track

A productivity tool that gently reminds you every 15 minutes to log your current activity. Designed to be unobtrusive, it lives in your system tray and helps you keep track of your workday with minimal friction.

## Key Features

- **Quarter-Hour Intervals**: Aligns reminders to clock time (:00, :15, :30, :45).
- **System Tray Integration**: Quietly runs in the background. Shows the next scheduled reminder time.
- **Activity History**: View today's logged activities directly from the app.
- **Local Storage**: Data is saved securely in CSV format in your Documents folder.
- **Auto-Start**: Includes a simple script to launch automatically with Windows.

## Installation

### Prerequisites
- Python 3.10 or higher
- Windows OS (Tested on Windows 10/11)

### Setup

1.  **Clone the Repository** (or download the source):
    ```bash
    git clone <repository-url>
    cd Stay-On-Track
    ```

2.  **Create Virtual Environment & Install Dependencies**:
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python src/main.py
    ```

4.  **Enable Auto-Start (Optional)**:
    Run the included PowerShell script to create a startup shortcut:
    ```powershell
    powershell -ExecutionPolicy Bypass -File .\install_autostart.ps1
    ```

## Usage

- **Logging**: When the popup appears, type your activity and press Enter.
- **Menu**: Right-click the system tray icon (Black/Green square) to:
    - See the **Next Reminder** time.
    - **Log Activity** manually.
    - **Show History** of today's entries.
    - Change **Settings** (Start/End time).
    - **Exit** the application.

## Data Location

Logs are stored in: `C:\Users\<YOU>\Documents\StayOnTrack\`

## Technologies

- **Python**: Core logic.
- **CustomTkinter**: Modern GUI framework.
- **Pystray**: System tray integration.
- **Pillow**: Image handling for icons.

## License

MIT License.
