# Typing Trainer Pro

A professional desktop typing trainer built with PySide6 (Qt for Python).

## Features

- **Animated 10-finger overlay** — correct finger slides to target key, then returns home
- **Real-time stats** — live WPM, accuracy, error count, best WPM, and mini sparkline
- **Countdown timer** — 15s / 30s / 1min / 2min — drift-free via `QElapsedTimer`
- **Difficulty levels** — Easy / Medium / Hard sentence generation (no external files)
- **Custom text** — paste any text via dialog
- **Practice modes** — Beginner (full hints), Intermediate (key hints only), Advanced (no hints)
- **Session history** — last 5 sessions in compact table
- **Keyboard shortcuts** — Space/Enter = Start · Esc = Reset · Tab = Next sentence
- **Slim notification strip** — replaces intrusive warning banner

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
python -m typing_trainer.main
```

Or run directly:
```bash
python src/typing_trainer/main.py
```

## Building Executable

```bash
pip install pyinstaller
python -m PyInstaller --name "TypingTrainerPro" --windowed --onefile \
  --add-data "src/typing_trainer/ui/styles.qss;typing_trainer/ui" \
  --add-data "src/typing_trainer/core;typing_trainer/core" \
  --add-data "src/typing_trainer/services;typing_trainer/services" \
  src/typing_trainer/main.py
```

Output: `dist/TypingTrainerPro.exe`

## Project Structure

```
typing_trainer/
├── src/
│   └── typing_trainer/
│       ├── __init__.py
│       ├── main.py                 # Entry point
│       ├── core/                   # Pure-Python logic (no Qt)
│       │   ├── __init__.py
│       │   ├── typing_engine.py    # Character-level diff
│       │   ├── stats_calculator.py # WPM / accuracy formulas
│       │   └── sentence_generator.py
│       ├── services/               # Qt-dependent services
│       │   ├── __init__.py
│       │   ├── timer_service.py    # Drift-free countdown
│       │   └── stats_tracker.py    # Real-time stats aggregator
│       └── ui/                     # All widgets & styles
│           ├── __init__.py
│           ├── main_window.py      # MainWindow — central controller
│           ├── keyboard_widget.py  # VirtualKeyboard + FingerOverlay
│           ├── finger_widget.py    # Animated hand overlay
│           ├── mapping.py          # Key→finger data, colours, layouts
│           └── styles.qss          # Dark blue/purple theme
├── tests/                          # Unit tests
├── docs/                           # Documentation
├── assets/                         # Icons, images
├── scripts/                        # Build/deploy scripts
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Finger Map

| Finger | Keys |
|--------|------|
| Left Pinky | ` 1 Q A Z Tab Caps LShift |
| Left Ring | 2 W S X |
| Left Middle | 3 E D C |
| Left Index | 4 5 R T F G V B |
| Right Index | 6 7 Y U H J N M |
| Right Middle | 8 I K , |
| Right Ring | 9 O L . |
| Right Pinky | 0 - = P [ ] \ ; ' / Enter Backspace RShift |
| Both Thumbs | Space |

## Requirements

- Python 3.10+
- PySide6 >= 6.6.0

## License

MIT