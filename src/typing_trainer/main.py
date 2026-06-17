"""
main.py — Typing Trainer Pro v7
================================
Entry point — initialises config, database, logging, and global error handling.
"""

import sys

from PySide6.QtWidgets import QApplication, QMessageBox
from rich.console import Console

from typing_trainer.config.settings import load_settings
from typing_trainer.logging_setup import get_logger, setup_logging
from typing_trainer.storage.database import close_db, init_db
from typing_trainer.ui.main_window import MainWindow

logger = get_logger(__name__)


def _global_exception_handler(exc_type, exc_value, exc_traceback) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    Console(stderr=True).print_exception()
    QMessageBox.critical(
        None,
        "Typing Trainer Pro — Unexpected Error",
        f"{exc_type.__name__}: {exc_value}",
    )


def _init_application() -> QApplication:
    app = QApplication(sys.argv)
    app.setApplicationName("Typing Trainer Pro")
    app.setApplicationVersion("7.0")

    settings = load_settings()
    if settings.theme == "dark":
        app.setStyle("Fusion")
    return app


def main() -> None:
    setup_logging()
    sys.excepthook = _global_exception_handler

    logger.info("Starting Typing Trainer Pro")
    try:
        init_db()
        logger.info("Database initialised")
    except Exception:
        logger.warning("Database initialisation failed — continuing without persistence")

    app = _init_application()
    window = MainWindow()
    window.show()
    exit_code = app.exec()

    close_db()
    logger.info("Shutdown complete")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
