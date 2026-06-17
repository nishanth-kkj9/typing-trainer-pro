# Typing Trainer Pro

[![CI](https://github.com/nishanth-kkj9/typing-trainer-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/nishanth-kkj9/typing-trainer-pro/actions/workflows/ci.yml)

A professional desktop typing trainer built with PySide6 (Qt for Python).

## Features

- **Animated 10-finger overlay** — correct finger slides to target key, then returns home
- **Real-time stats** — live WPM, CPM, net WPM, accuracy, error count, consistency, best WPM, and mini sparkline
- **Countdown timer** — 15s / 30s / 1min / 2min — drift-free via `QElapsedTimer`, with pause/resume support
- **Difficulty levels** — Easy / Medium / Hard sentence generation with expanded word pools and punctuation
- **Custom text** — paste any text via dialog
- **Practice modes** — Beginner (full hints), Intermediate (key hints only), Advanced (no hints)
- **Session history** — last 5 sessions in compact table
- **Keyboard shortcuts** — Space/Enter = Start, Esc = Reset, Tab = Next sentence
- **Slim notification strip** — replaces intrusive warning banner
- **Persistent storage** — SQLite via SQLModel for sessions, users, and per-key statistics
- **Configurable settings** — TOML-backed persistent config for difficulty, theme, timer, sound, animations
- **Structured logging** — structlog with rotating file handler
- **Comprehensive error handling** — custom exception hierarchy with global crash dialog

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick start

```bash
# 1) create venv
python -m venv venv

# 2) activate (Windows)
venv\Scripts\activate

# 3) install deps
pip install -r requirements.txt

# 4) run the app
python -m typing_trainer.main
```

## Running

```bash
python -m typing_trainer.main
```

Or run directly (from repo root):

```bash
python src/typing_trainer/main.py
```


## Configuration

Settings are backed by TOML (see `src/typing_trainer/config/defaults.toml`).

## Building Executable

```bash
pip install pyinstaller
python -m PyInstaller --name "TypingTrainerPro" --windowed --onefile \
  --add-data "src/typing_trainer/ui/styles.qss;typing_trainer/ui" \
  --add-data "src/typing_trainer/config/defaults.toml;typing_trainer/config" \
  src/typing_trainer/main.py
```

Output: `dist/TypingTrainerPro.exe`


## Project Structure

```
typing_trainer/
├── src/
│   └── typing_trainer/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py                  # App bootstrap, exception handler
│       ├── config/                 # Persistent settings (TOML + pydantic-settings)
│       │   ├── __init__.py
│       │   ├── defaults.toml
│       │   └── settings.py
│       ├── core/                   # Pure-Python business logic (no Qt)
│       │   ├── __init__.py
│       │   ├── typing_engine.py    # Character-level diff with backspace/case support
│       │   ├── stats_calculator.py # WPM/CPM/accuracy/consistency/error rates
│       │   └── sentence_generator.py # Sentence generation (templates / topics / symbols)

│       ├── services/                # Qt-dependent services
│       │   ├── __init__.py
│       │   ├── timer_service.py     # Drift-free countdown with pause/resume
│       │   └── stats_tracker.py     # Real-time stats aggregator (signals)
│       ├── storage/                 # Persistence layer (SQLite + SQLModel)
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── models.py
│       │   └── repositories.py
│       ├── exceptions.py            # Custom exception hierarchy
│       ├── logging_setup.py         # Structured logging setup
│       ├── lessons/                 # Structured typing curriculum
│       │   └── data/
│       └── ui/                      # All Qt widgets
│           ├── __init__.py
│           ├── main_window.py       # Central controller
│           ├── keyboard_widget.py   # Virtual QWERTY keyboard
│           ├── mapping.py           # Key->finger data (pure data)
│           └── styles.qss           # Dark blue/purple theme
├── tests/                           # Test suite (126+ tests)
│   ├── __init__.py
│   ├── unit/                        # Unit tests for core & services
│   ├── integration/                 # Integration tests
│   └── fixtures/                    # Test fixtures
├── docs/                            # Documentation
│   ├── architecture.md
│   └── contributing.md
├── assets/                          # Icons, images, themes
├── scripts/                         # Build/deploy scripts
├── .github/workflows/              # CI/CD (lint, test, build, release)
├── pyproject.toml
├── requirements.txt
└── LICENSE
```


## Running Tests

```bash
# All tests
python -m pytest

# With coverage
python -m pytest --cov=typing_trainer --cov-report=term-missing

# Specific test file
python -m pytest tests/unit/test_typing_engine.py -v
```

## Code Quality

```bash
# Lint
python -m ruff check

# Type check
python -m mypy src/typing_trainer
```

## Requirements

- Python 3.10+
- PySide6 >= 6.6.0

## License

MIT
