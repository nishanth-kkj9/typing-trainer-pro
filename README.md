# Typing Trainer Pro

[![CI](https://github.com/nishanth-kkj9/typing-trainer-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/nishanth-kkj9/typing-trainer-pro/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A **professional desktop typing trainer** with modern UI, real-time analytics, and gamified progress tracking. Built with PySide6 (Qt for Python).

![Typing Trainer Pro](assets/screenshot.png)

## ✨ Features

### Core Training
- **🎯 Animated 10-finger overlay** — Visual finger guidance slides to target keys and returns home
- **⚡ Real-time stats dashboard** — Live WPM, CPM, net WPM, accuracy, error count, consistency, best WPM with mini sparkline charts
- **⏱️ Countdown timer** — 15s / 30s / 1min / 2min modes with drift-free `QElapsedTimer` and pause/resume support
- **📊 Difficulty levels** — Easy / Medium / Hard with expanded word pools and punctuation
- **📝 Custom text mode** — Paste any text for practice via dialog
- **🎓 Practice modes** — Beginner (full hints), Intermediate (key hints only), Advanced (no hints)

### Gamification & Progress
- **🔥 Daily streaks** — Track consecutive practice days with visual fire indicators
- **🏆 Achievement system** — Unlock 8 badges (Speed Demon, Perfectionist, Marathoner, etc.)
- **🎯 Daily goals** — Set and track daily WPM/time targets
- **📈 Session history** — View last 5 sessions with detailed metrics in compact table
- **💾 CSV export** — Export progress data for external analysis
- **👤 User profiles** — Persistent progress tracking across sessions

### Desktop App Experience
- **🎨 Modern dark theme** — Professional navy/purple gradient design inspired by VS Code & Discord
- **🔔 Desktop notifications** — Reminder alerts for daily practice goals
- **🔊 Sound effects** — Audio feedback for keypresses and achievements
- **⌨️ Keyboard shortcuts** — Space/Enter (Start), Esc (Reset), Tab (Next sentence)
- **📋 Context menus** — Right-click access to settings and export options
- **💻 Native feel** — Styled scrollbars, dialogs, tooltips, and menu bars

### Technical Excellence
- **💾 Persistent storage** — SQLite via SQLModel for sessions, users, and per-key statistics
- **⚙️ Configurable settings** — TOML-backed config for difficulty, theme, timer, sound, animations
- **🪵 Structured logging** — `structlog` with rotating file handler for debugging
- **🛡️ Comprehensive error handling** — Custom exception hierarchy with global crash dialog
- **✅ 126+ automated tests** — Unit, integration, and fixture coverage

## 🖼️ Screenshots

### Main Interface
![Main Interface](assets/main_screen.png)
*Modern dark theme with real-time stats and animated finger guidance*

### Progress Dashboard
![Progress](assets/progress_dashboard.png)
*Track your daily streaks, achievements, and session history*

### Settings Panel
![Settings](assets/settings.png)
*Customize difficulty, timer duration, sound effects, and visual preferences*

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/nishanth-kkj9/typing-trainer-pro.git
cd typing-trainer-pro

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
# Method 1: Module execution (recommended)
python -m typing_trainer.main

# Method 2: Direct script execution
python src/typing_trainer/main.py
```

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` / `Enter` | Start/Pause test |
| `Esc` | Reset current session |
| `Tab` | Skip to next sentence |
| `Ctrl+S` | Save session manually |
| `Ctrl+E` | Export progress to CSV |
| `Ctrl+,` | Open settings |
| `F1` | Show help dialog |

## 🎮 How to Use

1. **Select Difficulty**: Choose Easy, Medium, or Hard from the dropdown
2. **Choose Timer**: Pick 15s, 30s, 1min, or 2min duration
3. **Practice Mode**: Select Beginner, Intermediate, or Advanced
4. **Start Typing**: Press Space or click "Start" and begin typing the displayed sentence
5. **Watch Your Stats**: Real-time WPM, accuracy, and finger guidance update as you type
6. **Review Results**: After completion, view detailed metrics and session history
7. **Track Progress**: Check daily streaks and unlock achievements over time

## ⚙️ Configuration

Settings are stored in TOML format at `~/.local/typing-trainer-pro/config.toml`.

| Setting | Default | Description |
|---------|---------|-------------|
| `difficulty` | "medium" | Sentence complexity level |
| `timer_duration` | 60 | Test duration in seconds |
| `practice_mode` | "intermediate" | Hint display level |
| `theme` | "dark" | UI color theme |
| `sound_enabled` | true | Enable sound effects |
| `animations_enabled` | true | Enable finger animations |
| `daily_goal_wpm` | 40 | Target WPM for daily goals |
| `daily_goal_minutes` | 10 | Target practice minutes per day |

Edit manually or use the in-app Settings dialog (`Ctrl+,`).

## 📦 Building Desktop Executable

Create a standalone executable for distribution (no Python installation required):

### Option 1: Using Build Script (Recommended)

```bash
pip install pyinstaller
python build_app.py
```

### Option 2: Manual PyInstaller Command

```bash
pip install pyinstaller
python -m PyInstaller --name "TypingTrainerPro" --windowed --onefile \
  --add-data "src/typing_trainer/ui/styles.qss;typing_trainer/ui" \
  --add-data "src/typing_trainer/config/defaults.toml;typing_trainer/config" \
  src/typing_trainer/main.py
```

**Output**: 
- Windows: `dist/TypingTrainerPro.exe`
- macOS: `dist/TypingTrainerPro.app`
- Linux: `dist/TypingTrainerPro`

### Platform-Specific Notes

**Windows:**
```bash
# Add icon if available
--icon=assets/icon.ico
```

**macOS:**
```bash
# Create .app bundle with icon
python -m PyInstaller --windowed --icon=assets/icon.icns ...
```

**Linux:**
```bash
# Create desktop entry after building
sudo cp dist/TypingTrainerPro /usr/local/bin/
echo "[Desktop Entry]
Type=Application
Name=Typing Trainer Pro
Exec=TypingTrainerPro
Icon=typing-trainer-pro
Categories=Education;" | sudo tee /usr/share/applications/typing-trainer-pro.desktop
```

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=typing_trainer --cov-report=term-missing --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_typing_engine.py -v

# Run tests with verbose output
python -m pytest -vv
```

Coverage report will be generated in `htmlcov/` directory. Open `htmlcov/index.html` in browser to view.

## 🔍 Code Quality

```bash
# Lint with Ruff
python -m ruff check src/typing_trainer

# Type checking with MyPy
python -m mypy src/typing_trainer

# Format code with Black
python -m black src/typing_trainer tests

# Run all quality checks
python -m ruff check && python -m mypy src/typing_trainer && python -m black --check src/typing_trainer tests
```

## 🏗️ Project Structure

```
typing_trainer/
├── src/typing_trainer/
│   ├── __init__.py
│   ├── __main__.py              # Entry point for python -m
│   ├── main.py                  # App bootstrap & exception handler
│   ├── features.py              # Gamification (achievements, streaks, goals)
│   │
│   ├── config/                  # Settings management
│   │   ├── __init__.py
│   │   ├── defaults.toml        # Default configuration values
│   │   └── settings.py          # Pydantic settings class
│   │
│   ├── core/                    # Business logic (no Qt dependencies)
│   │   ├── __init__.py
│   │   ├── typing_engine.py     # Character-level diff & input handling
│   │   ├── stats_calculator.py  # WPM/CPM/accuracy/consistency calculations
│   │   └── sentence_generator.py # Dynamic sentence generation
│   │
│   ├── services/                # Qt-dependent services
│   │   ├── __init__.py
│   │   ├── timer_service.py     # Drift-free countdown timer
│   │   ├── stats_tracker.py     # Real-time stats aggregator
│   │   └── notification_service.py # Desktop notifications
│   │
│   ├── storage/                 # Persistence layer
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite connection & migrations
│   │   ├── models.py            # SQLModel ORM definitions
│   │   └── repositories.py      # Data access layer
│   │
│   ├── ui/                      # Qt widgets & styling
│   │   ├── __init__.py
│   │   ├── main_window.py       # Main application window
│   │   ├── keyboard_widget.py   # Virtual QWERTY keyboard
│   │   ├── mapping.py           # Key-to-finger mapping data
│   │   └── styles.qss           # Dark theme stylesheet
│   │
│   ├── exceptions.py            # Custom exception hierarchy
│   └── logging_setup.py         # Structured logging configuration
│
├── tests/                       # Test suite (126+ tests)
│   ├── unit/                    # Unit tests for core logic
│   ├── integration/             # Integration tests
│   └── fixtures/                # Shared test fixtures
│
├── assets/                      # Icons, screenshots, themes
├── docs/                        # Documentation
│   ├── architecture.md
│   └── contributing.md
├── scripts/                     # Build & deployment scripts
├── .github/workflows/           # CI/CD pipelines
├── build_app.py                 # PyInstaller build script
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 🛠️ Requirements

- **Python**: 3.10 or higher
- **Qt Bindings**: PySide6 >= 6.6.0
- **Database**: SQLite3 (built-in)
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)

### Dependencies

See `requirements.txt` for full list. Key packages:
- `pyside6` - Qt GUI framework
- `sqlmodel` - Database ORM
- `pydantic-settings` - Configuration management
- `structlog` - Structured logging
- `toml` - Configuration file parsing
- `pytest` - Testing framework

## 🐛 Troubleshooting

### Common Issues

**Issue**: App crashes on startup with "module not found"
- **Solution**: Ensure virtual environment is activated and dependencies installed: `pip install -r requirements.txt`

**Issue**: Database errors or missing sessions
- **Solution**: Delete old database and restart: `rm ~/.local/typing-trainer-pro/typing_trainer.db`

**Issue**: No sound playing
- **Solution**: Check system volume and ensure sound files exist in `assets/sounds/`

**Issue**: High CPU usage during idle
- **Solution**: Disable animations in Settings or reduce timer refresh rate

**Issue**: Blurry text on HiDPI displays
- **Solution**: Set environment variable before running:
  - Windows: `set QT_AUTO_SCREEN_SCALE_FACTOR=1`
  - macOS/Linux: `export QT_AUTO_SCREEN_SCALE_FACTOR=1`

### Getting Help

1. Check existing issues on [GitHub Issues](https://github.com/nishanth-kkj9/typing-trainer-pro/issues)
2. Review logs at `~/.local/typing-trainer-pro/typing_trainer.log`
3. Run with debug logging: `python -m typing_trainer.main --debug`

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](docs/contributing.md) for details.

### Quick Start for Contributors

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/typing-trainer-pro.git
cd typing-trainer-pro

# Install dev dependencies
pip install -r requirements-dev.txt

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, run tests
python -m pytest

# Submit PR
git push origin feature/your-feature-name
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by classic typing tutor programs
- Built with [PySide6](https://doc.qt.io/qtforpython/)
- Testing powered by [pytest](https://docs.pytest.org/)
- Icons from [FontAwesome](https://fontawesome.com/) (if used)

## 📬 Contact

- **Repository**: [github.com/nishanth-kkj9/typing-trainer-pro](https://github.com/nishanth-kkj9/typing-trainer-pro)
- **Issues**: [Report a bug or request feature](https://github.com/nishanth-kkj9/typing-trainer-pro/issues)
- **Discussions**: [Community forum](https://github.com/nishanth-kkj9/typing-trainer-pro/discussions)

---

<div align="center">
  <strong>Typing Trainer Pro</strong> | Improve your typing speed and accuracy today!
</div>
