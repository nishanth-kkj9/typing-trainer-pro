"""
main.py — Typing Trainer Pro v7
================================
Combined & improved version merging v5 (package structure) and v6 (animated finger overlay).

Run:
    python main.py
"""

import sys

from PySide6.QtWidgets import QApplication

from typing_trainer.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Typing Trainer Pro")
    app.setApplicationVersion("7.0")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
