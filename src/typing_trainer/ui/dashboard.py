from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QTabWidget, QVBoxLayout, QWidget,
)

from typing_trainer.storage.repositories import KeyStatRepository, TrainingSessionRepository
from typing_trainer.ui.chart_widgets import (
    AccuracyChartWidget,
    SessionDetailWidget,
    SessionsTableWidget,
    WpmChartWidget,
)


class DashboardWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Typing Trainer Pro — Progress Dashboard")
        self.resize(800, 600)

        self._apply_styles()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        toolbar = QHBoxLayout()
        self.refresh_btn = QPushButton("↻  Refresh")
        self.refresh_btn.setObjectName("secondaryBtn")
        self.refresh_btn.setFixedWidth(114)
        self.refresh_btn.clicked.connect(self._load_data)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_btn)
        layout.addLayout(toolbar)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.sessions_tab = SessionsTableWidget()
        self.detail_tab = SessionDetailWidget()
        self.charts_tab = QWidget()

        self.tabs.addTab(self.sessions_tab, "Sessions")
        self.tabs.addTab(self.detail_tab, "Session Detail")
        self.tabs.addTab(self.charts_tab, "Charts")

        self._setup_charts_tab()
        self._setup_detail_tab()
        self._load_data()

    def _setup_charts_tab(self) -> None:
        layout = QVBoxLayout(self.charts_tab)
        layout.addWidget(QLabel("WPM Progression"))
        self.wpm_chart = WpmChartWidget()
        layout.addWidget(self.wpm_chart)
        layout.addWidget(QLabel("Accuracy Trend"))
        self.accuracy_chart = AccuracyChartWidget()
        layout.addWidget(self.accuracy_chart)

    def _setup_detail_tab(self) -> None:
        self.sessions_tab.table.itemSelectionChanged.connect(self._on_session_selected)

    def _load_data(self) -> None:
        repo = TrainingSessionRepository()
        sessions = repo.get_all()
        if not sessions:
            return

        rows = []
        wpm_values = []
        acc_values = []
        labels = []
        for s in sessions:
            row = {
                "id": s.id,
                "started_at": str(s.started_at),
                "difficulty": s.difficulty or "",
                "wpm": s.wpm or 0,
                "accuracy": s.accuracy or 0,
                "errors": s.errors or 0,
                "duration_seconds": s.duration_seconds or 0,
                "mode": s.mode or "",
                "correct": s.correct or 0,
            }
            rows.append(row)
            wpm_values.append(s.wpm or 0)
            acc_values.append(s.accuracy or 0)
            labels.append(str(s.id))

        self.sessions_tab.set_sessions(rows)
        self.wpm_chart.set_data(wpm_values, labels)
        self.accuracy_chart.set_data(acc_values, labels)

    def _enable_windows_11_native(self) -> None:
        try:
            import ctypes
            hwnd = int(self.winId())
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 1029, ctypes.byref(value), ctypes.sizeof(value)
            )
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
            )
        except Exception:
            pass

    def _apply_styles(self) -> None:
        p = Path(__file__).parent / "styles.qss"
        if p.exists():
            self.setStyleSheet(p.read_text(encoding="utf-8"))

    def _on_session_selected(self) -> None:
        selected = self.sessions_tab.table.currentRow()
        if selected < 0:
            return
        repo = TrainingSessionRepository()
        sessions = repo.get_all()
        if selected >= len(sessions):
            return
        session = sessions[selected]
        self.detail_tab.set_session({
            "wpm": session.wpm or 0,
            "accuracy": session.accuracy or 0,
            "errors": session.errors or 0,
            "duration_seconds": session.duration_seconds or 0,
            "difficulty": session.difficulty or "",
            "mode": session.mode or "",
            "correct": session.correct or 0,
        })
        if session.id:
            ks_repo = KeyStatRepository()
            key_stats = ks_repo.get_by_session(session.id)
            self.detail_tab.set_key_stats([
                {"key_char": ks.key_char, "correct_count": ks.correct_count, "error_count": ks.error_count}
                for ks in key_stats
            ])
