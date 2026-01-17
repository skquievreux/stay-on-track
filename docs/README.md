# Stay-On-Track Documentation

Welcome to the Stay-On-Track documentation! This guide will help you install, use, and contribute to the project.

## 📚 Documentation Structure

### For Users

#### [Installation Guide](01-architecture/INSTALLER_GUIDE.md)
- Windows installer walkthrough
- Manual installation
- System requirements
- Uninstallation

#### [User Guide](02-implementation/user-guide.md)
- Getting started
- Daily usage
- Viewing your data
- Configuration
- Tips & tricks

#### [Analytics & Categories](02-implementation/analytics.md)
- Understanding the 9 categories
- Auto-learning system
- Interpreting analytics
- Customizing keywords

#### [Troubleshooting](03-operations/troubleshooting.md)
- Common issues
- Error messages
- Performance problems
- Data recovery
- Getting help

### For Developers

#### [Architecture Overview](01-architecture/OVERVIEW.md)
- Core components
- Data flow
- System design

#### [Best Practices](02-implementation/BEST_PRACTICES.md)
- Local development
- Code quality standards
- Git workflow
- CI/CD pipeline

#### [Distribution Guide](02-implementation/DISTRIBUTION.md)
- Building from source
- Creating installers
- Release process

#### [Code Signing](02-implementation/CODE_SIGNING.md)
- Certificate setup
- Signing process
- Verification

## 🚀 Quick Start

### For End Users

1. **Download** the installer from [Releases](https://github.com/skquievreux/stay-on-track/releases)
2. **Run** `StayOnTrack_Setup_v*.exe`
3. **Configure** your active hours
4. **Start tracking!**

### For Developers

```bash
# Clone repository
git clone https://github.com/skquievreux/stay-on-track.git
cd stay-on-track

# Install Poetry
pipx install poetry

# Install dependencies
poetry install

# Run application
poetry run python src/main.py
```

## 📖 Key Features

- ⏰ **15-Minute Reminders** - Aligned to quarter-hour intervals
- 💾 **Daily CSV Logs** - Automatic storage
- 🔔 **Sound Notifications** - Audio alerts
- 📊 **Multi-Day Analytics** - View statistics for 7 or 30 days
- 🎨 **Activity Clustering** - Automatic categorization into 9 categories
- 🤖 **Auto-Learning** - Discovers patterns from your activities

## 🗂️ Project Structure

```
Stay-On-Track/
├── src/                    # Python source code
│   ├── main.py            # Application entry point
│   ├── ui.py              # UI components
│   ├── storage.py         # Data persistence
│   ├── scheduler.py       # Reminder scheduling
│   ├── analytics.py       # Analytics engine
│   └── category_engine.py # Activity categorization
├── docs/                   # Documentation (you are here!)
│   ├── 01-architecture/   # System design
│   ├── 02-implementation/ # User & developer guides
│   └── 03-operations/     # Troubleshooting & support
├── .github/workflows/      # CI/CD pipelines
├── build.spec             # PyInstaller configuration
├── setup_script.iss       # Inno Setup installer script
└── pyproject.toml         # Poetry dependencies
```

## 🤝 Contributing

We welcome contributions! Please see:
- [Best Practices](02-implementation/BEST_PRACTICES.md) for development guidelines
- [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution workflow
- [GitHub Issues](https://github.com/skquievreux/stay-on-track/issues) for open tasks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Support

- **Documentation:** You're reading it!
- **Issues:** [GitHub Issues](https://github.com/skquievreux/stay-on-track/issues)
- **Discussions:** [GitHub Discussions](https://github.com/skquievreux/stay-on-track/discussions)

---

**Made with ❤️ for better productivity tracking**

**Version:** 1.3.x | **Last Updated:** 2026-01-17
