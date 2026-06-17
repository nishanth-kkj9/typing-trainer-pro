# Typing Trainer Pro — Architecture

## Overview

Desktop typing trainer built with PySide6 (Qt 6 for Python).
Follows a layered architecture with strict separation of concerns.

```
src/typing_trainer/
├── __init__.py, __main__.py   # Package entry points
├── main.py                    # App bootstrap, exception handler
├── config/                    # Pydantic-based settings (persistent TOML)
├── core/                      # Pure-Python business logic (no Qt)
│   ├── typing_engine.py       # Character-level diff engine
│   ├── stats_calculator.py    # WPM/accuracy/error formulas
│   └── sentence_generator.py  # Template-based sentence generation
├── storage/                   # Persistence layer (SQLite + SQLModel)
│   ├── database.py            # Connection management, migrations
│   ├── models.py              # ORM models (User, Session, KeyStat)
│   └── repositories.py       # Data access objects
├── services/                  # Qt-dependent services
│   ├── timer_service.py       # Drift-free countdown (QElapsedTimer)
│   └── stats_tracker.py       # Real-time stats aggregator (signals)
├── lessons/                   # Structured typing curriculum
│   ├── curriculum.py          # Lesson definitions & progression
│   ├── lesson_engine.py       # Completion tracking, unlocks
│   └── data/                  # Lesson JSON files
├── ui/                        # All Qt widgets
│   ├── main_window.py         # Central controller
│   ├── keyboard_widget.py     # Virtual QWERTY keyboard
│   ├── finger_widget.py       # Animated hand overlay
│   ├── mapping.py             # Key→finger data (pure data)
│   ├── styles.qss             # Dark blue/purple theme
│   └── layouts/               # Multi-language keyboard layouts
└── storage/migrations/        # Alembic migrations
```

## Layers

### Core (no Qt dependency)
Pure Python, fully unit-testable. All business logic lives here.

### Services (Qt-dependent)
Thin service layer. Depends on core + PySide6. Emit Qt signals.

### UI
Qt widgets. Depends on core + services. No business logic.

### Storage
Data access via SQLModel (SQLite). Migrations via Alembic.

### Config
Pydantic Settings backed by TOML files. Hot-reload capable.

## Data Flow

User Input → MainWindow → StatsTracker → StatsCalculator → StatsChanged signal
                           → TypingEngine → Display + Keyboard highlights
                           → TimerService → Time tick → Elapsed signal

## Testing Strategy

- **Unit tests** (pytest): core/ and services/ — mock Qt signals
- **Integration tests** (pytest-qt): UI component interactions
- **Coverage target**: ≥80%
