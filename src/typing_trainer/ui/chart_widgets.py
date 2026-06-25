from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class SessionsTableWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Difficulty", "WPM", "Accuracy", "Errors", "Duration"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)

    def set_sessions(self, sessions: list[dict]) -> None:
        self.table.setRowCount(len(sessions))
        for row, s in enumerate(sessions):
            self.table.setItem(row, 0, QTableWidgetItem(str(s.get("started_at", ""))[:19]))
            self.table.setItem(row, 1, QTableWidgetItem(s.get("difficulty", "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(round(s.get("wpm", 0), 1))))
            self.table.setItem(row, 3, QTableWidgetItem(f'{s.get("accuracy", 0):.1f}%'))
            self.table.setItem(row, 4, QTableWidgetItem(str(s.get("errors", 0))))
            dur = s.get("duration_seconds", 0)
            self.table.setItem(row, 5, QTableWidgetItem(f"{int(dur // 60)}:{int(dur % 60):02d}"))


class WpmChartWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._data: list[float] = []
        self._session_labels: list[str] = []
        self.setMinimumHeight(200)

    def set_data(self, values: list[float], labels: list[str] | None = None) -> None:
        self._data = values
        self._session_labels = labels or [str(i) for i in range(len(values))]
        self.update()

    def paintEvent(self, _event) -> None:
        if not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin = 40
        chart_w = w - 2 * margin
        chart_h = h - 2 * margin

        max_val = max(self._data) * 1.1 or 1.0
        bar_w = chart_w / len(self._data) * 0.6
        gap = chart_w / len(self._data) * 0.4

        for i, val in enumerate(self._data):
            x = margin + i * (bar_w + gap)
            bar_h = (val / max_val) * chart_h
            y = h - margin - bar_h

            p.setBrush(QColor("#4fc3f7"))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(int(x), int(y), int(bar_w), int(bar_h), 3, 3)

        p.setPen(QPen(QColor("#c8c8d4"), 1))
        p.setFont(self.font())
        for i in range(0, len(self._data), max(1, len(self._data) // 10)):
            x = margin + i * (bar_w + gap) + bar_w / 2 - 10
            p.drawText(int(x), h - 5, 30, 12, Qt.AlignCenter, self._session_labels[i] if i < len(self._session_labels) else "")


class SessionDetailWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.summary_group = QGroupBox("Session Summary")
        self.summary_layout = QFormLayout(self.summary_group)
        self._fields: dict[str, QLabel] = {}
        for label in ("WPM", "Accuracy", "Errors", "Duration", "Difficulty", "Mode", "Correct"):
            lbl = QLabel("—")
            self._fields[label] = lbl
            self.summary_layout.addRow(f"{label}:", lbl)
        layout.addWidget(self.summary_group)

        self.key_table = QTableWidget()
        self.key_table.setColumnCount(3)
        self.key_table.setHorizontalHeaderLabels(["Key", "Correct", "Errors"])
        self.key_table.horizontalHeader().setStretchLastSection(True)
        self.key_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(QLabel("Per-Key Stats:"))
        layout.addWidget(self.key_table)

    def set_session(self, session: dict) -> None:
        self._fields["WPM"].setText(str(round(session.get("wpm", 0), 1)))
        self._fields["Accuracy"].setText(f'{session.get("accuracy", 0):.1f}%')
        self._fields["Errors"].setText(str(session.get("errors", 0)))
        dur = session.get("duration_seconds", 0)
        self._fields["Duration"].setText(f"{int(dur // 60)}:{int(dur % 60):02d}")
        self._fields["Difficulty"].setText(session.get("difficulty", ""))
        self._fields["Mode"].setText(session.get("mode", ""))
        self._fields["Correct"].setText(str(session.get("correct", 0)))

    def set_key_stats(self, key_stats: list[dict]) -> None:
        self.key_table.setRowCount(len(key_stats))
        for row, ks in enumerate(key_stats):
            self.key_table.setItem(row, 0, QTableWidgetItem(ks.get("key_char", "")))
            self.key_table.setItem(row, 1, QTableWidgetItem(str(ks.get("correct_count", 0))))
            self.key_table.setItem(row, 2, QTableWidgetItem(str(ks.get("error_count", 0))))


class AccuracyChartWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._data: list[float] = []
        self._session_labels: list[str] = []
        self.setMinimumHeight(200)

    def set_data(self, values: list[float], labels: list[str] | None = None) -> None:
        self._data = values
        self._session_labels = labels or [str(i) for i in range(len(values))]
        self.update()

    def paintEvent(self, _event) -> None:
        if len(self._data) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin = 40
        chart_w = w - 2 * margin
        chart_h = h - 2 * margin

        lo, hi = 90, 100
        span = hi - lo or 1.0
        n = len(self._data)
        xs = [margin + i / (n - 1) * chart_w for i in range(n)]
        ys = [h - margin - ((v - lo) / span) * chart_h for v in self._data]

        pen = QPen(QColor("#4ade80"), 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        for i in range(n - 1):
            p.drawLine(int(xs[i]), int(ys[i]), int(xs[i + 1]), int(ys[i + 1]))

        p.setPen(QPen(QColor("#c8c8d4"), 1))
        p.drawText(5, h - margin + 5, 30, 12, Qt.AlignCenter, "90%")
        p.drawText(5, margin - 5, 30, 12, Qt.AlignCenter, "100%")
