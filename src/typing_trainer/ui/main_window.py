"""
ui/main_window.py — Typing Trainer Pro v7
==========================================
Combined and improved MainWindow merging v5 (package structure, sparkline,
session history, custom text, keyboard shortcuts) with v6 (animated finger
overlay, finger legend, improved keyboard widget, mapping module).

Features
--------
  • Animated 10-finger overlay — the correct finger slides to the target key
  • Real-time WPM / accuracy / error stats with live sparkline
  • Configurable countdown timer: 15 s / 30 s / 1 min / 2 min
  • Easy / Medium / Hard random sentence generation
  • Custom text mode (paste any text via dialog)
  • Beginner / Intermediate / Advanced practice modes
  • Session history: last 5 sessions in a compact table
  • Keyboard shortcuts: Space/Enter = Start, Esc = Reset, Tab = Next
  • Slim notification strip replaces old intrusive banner
  • Best WPM tracked and updated live
"""

import logging
import sys
from collections import deque
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import (
    QColor,
    QFontDatabase,
    QKeyEvent,
    QPainter,
    QPen,
    QTextCharFormat,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from typing_trainer.core.sentence_generator import SentenceGenerator
from typing_trainer.core.typing_engine import CharStatus, TypingEngine
from typing_trainer.services.stats_tracker import StatsTracker
from typing_trainer.services.timer_service import TimerService
from typing_trainer.ui.keyboard_widget import VirtualKeyboard

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _is_windows_11() -> bool:
    if sys.platform != "win32":
        return False
    try:
        ver = sys.getwindowsversion()
        return ver.build >= 22000
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  Sparkline — live WPM mini-chart inside the WPM stat card
# ─────────────────────────────────────────────────────────────────────────────

class Sparkline(QWidget):
    def __init__(self, maxlen: int = 60, parent=None) -> None:
        super().__init__(parent)
        self._data: deque[float] = deque(maxlen=maxlen)
        self.setFixedSize(82, 24)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def push(self, value: float) -> None:
        self._data.append(value)
        self.update()

    def clear(self) -> None:
        self._data.clear()
        self.update()

    def paintEvent(self, _event) -> None:
        if len(self._data) < 2:
            return
        p   = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pts = list(self._data)
        lo, hi = min(pts), max(pts)
        span   = hi - lo or 1.0
        w, h   = self.width(), self.height()
        pen    = QPen(QColor("#4fc3f7"), 1.4)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        n  = len(pts)
        xs = [i / (n - 1) * w for i in range(n)]
        ys = [h - ((v - lo) / span) * (h - 4) - 2 for v in pts]
        for i in range(n - 1):
            p.drawLine(int(xs[i]), int(ys[i]), int(xs[i+1]), int(ys[i+1]))


# ─────────────────────────────────────────────────────────────────────────────
#  Custom-text dialog
# ─────────────────────────────────────────────────────────────────────────────

class CustomTextDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Custom Practice Text")
        self.setMinimumSize(520, 240)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Paste or type the text you want to practise:"))
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Enter your text here…")
        layout.addWidget(self.editor)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def text(self) -> str:
        return self.editor.toPlainText().strip()


# ─────────────────────────────────────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    TIMER_DURATIONS = {"15 s": 15, "30 s": 30, "1 min": 60, "2 min": 120}
    MAX_HISTORY = 5

    # Practice mode IDs
    MODE_BEGINNER     = 0
    MODE_INTERMEDIATE = 1
    MODE_ADVANCED     = 2

    def __init__(self) -> None:
        super().__init__()
        self.generator   = SentenceGenerator()
        self.target_text = ""
        self.user_input  = ""
        self.engine: TypingEngine | None  = None
        self.timer       = TimerService(duration_seconds=60)
        self.stats_tracker: StatsTracker | None = None

        self.session_active  = False
        self._elapsed:       float = 0.0
        self._best_wpm:      float = 0.0
        self._session_history: list = []
        self._current_mode   = self.MODE_BEGINNER

        self.setWindowTitle("Typing Trainer Pro")
        self.resize(1240, 980)
        self._setup_ui()
        self._apply_styles()
        self._connect_signals()
        if _is_windows_11():
            QTimer.singleShot(0, self._enable_windows_11_native)
        self._generate_sentence("easy")
        self._refresh_history_ui()
        logger.info("MainWindow ready")

    # ── UI Construction ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(6)
        root.setContentsMargins(16, 10, 16, 8)

        # ── Header bar ──────────────────────────────────────────────────────
        hdr = QHBoxLayout(); hdr.setSpacing(8)

        title = QLabel("⌨  Typing Trainer Pro")
        title.setObjectName("appTitle")

        diff_lbl = QLabel("Difficulty:"); diff_lbl.setObjectName("sectionLabel")
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["easy", "medium", "hard"])
        self.difficulty_combo.setFixedWidth(92)

        dur_lbl = QLabel("Time:"); dur_lbl.setObjectName("sectionLabel")
        self.duration_combo = QComboBox()
        for lbl in self.TIMER_DURATIONS:
            self.duration_combo.addItem(lbl)
        self.duration_combo.setCurrentText("1 min")
        self.duration_combo.setFixedWidth(72)

        mode_lbl = QLabel("Mode:"); mode_lbl.setObjectName("sectionLabel")
        self.mode_group        = QButtonGroup(self)
        self.radio_beginner     = QRadioButton("Beginner")
        self.radio_intermediate = QRadioButton("Intermediate")
        self.radio_advanced     = QRadioButton("Advanced")
        self.radio_beginner.setChecked(True)
        self.mode_group.addButton(self.radio_beginner,     self.MODE_BEGINNER)
        self.mode_group.addButton(self.radio_intermediate, self.MODE_INTERMEDIATE)
        self.mode_group.addButton(self.radio_advanced,     self.MODE_ADVANCED)

        self.custom_btn   = QPushButton("✎  Custom Text")
        self.generate_btn = QPushButton("↺  New Sentence")
        self.custom_btn.setObjectName("secondaryBtn")
        self.generate_btn.setObjectName("secondaryBtn")
        self.custom_btn.setFixedWidth(114)
        self.generate_btn.setFixedWidth(122)

        self.dashboard_btn = QPushButton("📊  Dashboard")
        self.dashboard_btn.setObjectName("secondaryBtn")
        self.dashboard_btn.setFixedWidth(114)

        hdr.addWidget(title); hdr.addStretch()
        hdr.addWidget(diff_lbl); hdr.addWidget(self.difficulty_combo); hdr.addSpacing(6)
        hdr.addWidget(dur_lbl);  hdr.addWidget(self.duration_combo);   hdr.addSpacing(8)
        hdr.addWidget(mode_lbl)
        hdr.addWidget(self.radio_beginner)
        hdr.addWidget(self.radio_intermediate)
        hdr.addWidget(self.radio_advanced);  hdr.addSpacing(8)
        hdr.addWidget(self.custom_btn)
        hdr.addWidget(self.generate_btn)
        hdr.addWidget(self.dashboard_btn)
        root.addLayout(hdr)

        # ── Stats row ────────────────────────────────────────────────────────
        stats_row = QHBoxLayout(); stats_row.setSpacing(8)
        self._wpm_card  = self._stat_card("WPM",      "0",    "#4fc3f7", sparkline=True)
        self._acc_card  = self._stat_card("ACCURACY", "100%", "#4ade80")
        self._err_card  = self._stat_card("ERRORS",   "0",    "#f87171")
        self._best_card = self._stat_card("BEST WPM", "0",    "#fbbf24")
        for card in (self._wpm_card, self._acc_card, self._err_card, self._best_card):
            stats_row.addWidget(card, stretch=1)
        stats_row.addStretch(1)
        self.timer_label = QLabel("01:00")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setFixedWidth(132)
        stats_row.addWidget(self.timer_label)
        root.addLayout(stats_row)

        root.addWidget(self._separator())

        # ── Target text display ──────────────────────────────────────────────
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixed_font.setPointSize(15)

        self.display_text = QTextEdit()
        self.display_text.setReadOnly(True)
        self.display_text.setFont(fixed_font)
        self.display_text.setFixedHeight(104)
        self.display_text.setObjectName("displayText")
        root.addWidget(self.display_text)

        # ── Progress bar ─────────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100); self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6); self.progress_bar.setTextVisible(False)
        self.progress_bar.setObjectName("progressBar")
        root.addWidget(self.progress_bar)

        # ── Input box ────────────────────────────────────────────────────────
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Press  Space  or  Enter  to start, then type here…")
        self.input_box.setFont(fixed_font)
        self.input_box.setEnabled(False)
        self.input_box.setObjectName("inputBox")
        root.addWidget(self.input_box)

        # ── Notification strip ───────────────────────────────────────────────
        self.notif = QLabel("")
        self.notif.setObjectName("notifStrip")
        self.notif.setAlignment(Qt.AlignCenter)
        self.notif.setFixedHeight(30)
        self.notif.setVisible(False)
        root.addWidget(self.notif)

        # ── Virtual keyboard with finger overlay ─────────────────────────────
        self.keyboard = VirtualKeyboard()
        root.addWidget(self.keyboard)

        # ── Finger legend (Beginner mode only) ───────────────────────────────
        self.legend = self._build_legend()
        root.addWidget(self.legend)

        # ── Control buttons ──────────────────────────────────────────────────
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        self.start_btn = QPushButton("▶  Start  [Space]")
        self.reset_btn = QPushButton("↺  Reset  [Esc]")
        self.next_btn  = QPushButton("⏭  Next  [Tab]")
        self.start_btn.setObjectName("primaryBtn")
        self.reset_btn.setObjectName("secondaryBtn")
        self.next_btn.setObjectName("secondaryBtn")
        for b in (self.start_btn, self.reset_btn, self.next_btn):
            b.setFixedWidth(154)
        self.reset_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addWidget(self.next_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        # ── Session history ──────────────────────────────────────────────────
        root.addWidget(self._separator())
        hist_hdr = QHBoxLayout()
        hist_lbl = QLabel("Session History"); hist_lbl.setObjectName("histTitle")
        hist_hdr.addWidget(hist_lbl); hist_hdr.addStretch()
        root.addLayout(hist_hdr)

        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_layout.setSpacing(2)
        self.history_layout.setContentsMargins(0, 2, 0, 2)
        root.addWidget(self.history_widget)

    # ── Widget factories ───────────────────────────────────────────────────

    def _separator(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setObjectName("separator")
        return f

    def _stat_card(self, label: str, value: str,
                   colour: str, sparkline: bool = False) -> QFrame:
        frame = QFrame(); frame.setObjectName("statCard")
        lay   = QVBoxLayout(frame)
        lay.setContentsMargins(10, 5, 10, 5); lay.setSpacing(1)
        lbl = QLabel(label); lbl.setObjectName("statLabel")
        val = QLabel(value); val.setObjectName("statValue")
        val.setStyleSheet(f"color:{colour};font-size:22px;font-weight:800;")
        lay.addWidget(lbl, alignment=Qt.AlignCenter)
        lay.addWidget(val, alignment=Qt.AlignCenter)
        if sparkline:
            self._sparkline = Sparkline()
            lay.addWidget(self._sparkline, alignment=Qt.AlignCenter)
        frame._val = val
        return frame

    @staticmethod
    def _build_legend() -> QWidget:
        w = QWidget(); w.setFixedHeight(16)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(6, 0, 6, 0); lay.setSpacing(6)
        entries = [
            ("LP","#9b59b6"),("LR","#3498db"),("LM","#2ecc71"),("LI","#e67e22"),
            ("RI","#f1c40f"),("RM","#1abc9c"),("RR","#e74c3c"),("RP","#e84393"),
        ]
        for abbr, clr in entries:
            dot = QLabel()
            dot.setFixedSize(9, 9)
            dot.setStyleSheet(f"background:{clr};border-radius:4px;")
            lbl = QLabel(abbr)
            lbl.setStyleSheet(f"color:{clr};font-size:9px;font-weight:700;")
            lay.addWidget(dot); lay.addWidget(lbl)
        lay.addStretch()
        desc = QLabel(
            "LP=Left Pinky · LR=Ring · LM=Middle · LI=Index · "
            "RI=Right Index · RM=Middle · RR=Ring · RP=Pinky"
        )
        desc.setStyleSheet("color:#5a5a88;font-size:8px;")
        lay.addWidget(desc)
        return w

    def _set_stat(self, card: QFrame, text: str) -> None:
        card._val.setText(text)

    def _apply_styles(self) -> None:
        p = Path(__file__).parent / "styles.qss"
        if p.exists():
            self.setStyleSheet(p.read_text(encoding="utf-8"))

    # ── Windows 11 native ──────────────────────────────────────────────────

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

    # ── Signal wiring ──────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self.difficulty_combo.currentTextChanged.connect(self._on_difficulty_changed)
        self.duration_combo.currentTextChanged.connect(self._on_duration_changed)
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        self.custom_btn.clicked.connect(self._on_custom_clicked)
        self.dashboard_btn.clicked.connect(self._open_dashboard)
        self.start_btn.clicked.connect(self.start_session)
        self.reset_btn.clicked.connect(self.reset_session)
        self.next_btn.clicked.connect(self.next_sentence)
        self.input_box.textChanged.connect(self._on_user_input)
        self.mode_group.idClicked.connect(self._on_mode_changed)
        self.timer.time_updated.connect(self._on_time_updated)
        self.timer.elapsed_updated.connect(self._on_elapsed_updated)
        self.timer.timer_finished.connect(self._on_timer_expired)
        self.keyboard.key_pressed.connect(self._on_virtual_key)

    # ── Global keyboard shortcuts ──────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if not self.session_active:
            if key in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter):
                if self.start_btn.isEnabled() and self.start_btn.isVisible():
                    self.start_session(); return
            if key == Qt.Key_Tab:
                if self.next_btn.isEnabled():
                    self.next_sentence(); return
        if key == Qt.Key_Escape:
            if self.reset_btn.isEnabled():
                self.reset_session(); return
        super().keyPressEvent(event)

    # ── Sentence management ────────────────────────────────────────────────

    def _generate_sentence(self, difficulty: str) -> None:
        self.target_text = self.generator.generate(difficulty)
        self.user_input  = ""
        self._refresh_display()
        self._update_expected_key()

    @Slot()
    def _on_generate_clicked(self) -> None:
        if self.session_active:
            self.reset_session()
        self._generate_sentence(self.difficulty_combo.currentText())
        self.reset_btn.setEnabled(False)

    @Slot()
    def _on_custom_clicked(self) -> None:
        dlg = CustomTextDialog(self)
        if dlg.exec() == QDialog.Accepted:
            text = dlg.text()
            if text:
                self.target_text = text
                if self.session_active:
                    self.reset_session()
                self.user_input = ""
                self._refresh_display()
                self._update_expected_key()

    @Slot()
    def _open_dashboard(self) -> None:
        from typing_trainer.ui.dashboard import DashboardWindow
        self._dashboard_window = DashboardWindow(self)
        self._dashboard_window.show()
        if _is_windows_11():
            QTimer.singleShot(0, self._dashboard_window._enable_windows_11_native)

    @Slot(str)
    def _on_difficulty_changed(self, _: str) -> None:
        pass  # applied on next Generate or Start

    @Slot(str)
    def _on_duration_changed(self, label: str) -> None:
        secs = self.TIMER_DURATIONS.get(label, 60)
        self.timer.duration = secs
        if not self.session_active:
            self.timer.reset()
            self.timer_label.setText(f"{secs//60:02d}:{secs%60:02d}")

    @Slot(int)
    def _on_mode_changed(self, mode_id: int) -> None:
        self._current_mode = mode_id
        self.legend.setVisible(mode_id == self.MODE_BEGINNER)
        if mode_id == self.MODE_ADVANCED:
            self.keyboard.clear_highlights()
        else:
            self._update_expected_key()

    @Slot()
    def next_sentence(self) -> None:
        self._generate_sentence(self.difficulty_combo.currentText())
        self.reset_session()

    # ── Display helpers ────────────────────────────────────────────────────

    def _refresh_display(self) -> None:
        if not self.target_text:
            return
        self.display_text.clear()
        cursor = self.display_text.textCursor()

        if self.engine and self.session_active:
            statuses, cursor_pos = self.engine.compare(self.user_input)
        else:
            statuses   = [CharStatus.UNTYPED] * len(self.target_text)
            cursor_pos = -1

        fmt_ok    = QTextCharFormat(); fmt_ok.setForeground(QColor("#6fcf6f"))
        fmt_err   = QTextCharFormat(); fmt_err.setForeground(QColor("#ef5350")); fmt_err.setBackground(QColor("#3d1a1a"))
        fmt_cur   = QTextCharFormat(); fmt_cur.setBackground(QColor("#1a5fa8")); fmt_cur.setForeground(QColor("#ffffff"))
        fmt_plain = QTextCharFormat(); fmt_plain.setForeground(QColor("#c8c8d4"))

        for i, ch in enumerate(self.target_text):
            if i == cursor_pos:
                cursor.insertText(ch, fmt_cur)
            elif i < len(statuses):
                s = statuses[i]
                cursor.insertText(ch,
                    fmt_ok    if s == CharStatus.CORRECT   else
                    fmt_err   if s == CharStatus.INCORRECT else
                    fmt_plain
                )
            else:
                cursor.insertText(ch, fmt_plain)

    def _update_expected_key(self) -> None:
        if not self.target_text:
            return
        pos = 0
        if self.session_active and self.engine:
            _, pos = self.engine.compare(self.user_input)

        if pos < len(self.target_text):
            exp  = self.target_text[pos]
            nxt  = self.target_text[pos + 1] if pos + 1 < len(self.target_text) else None
            show = (self._current_mode != self.MODE_ADVANCED)
            self.keyboard.set_target(exp, nxt, show_highlights=show)
        else:
            self.keyboard.set_target(None)

    def _update_progress(self) -> None:
        if self.target_text:
            pct = min(int(len(self.user_input) / len(self.target_text) * 100), 100)
            self.progress_bar.setValue(pct)

    def _show_notif(self, text: str, kind: str = "warning") -> None:
        colours = {
            "warning": "background:#3d2000;color:#ffb74d;border:1px solid #7a4400;",
            "danger":  "background:#2d0f0f;color:#ef9a9a;border:1px solid #8b1a1a;",
            "success": "background:#0d2c1a;color:#81c784;border:1px solid #1a6035;",
        }
        self.notif.setText(text)
        self.notif.setStyleSheet(
            "font-size:12px;font-weight:600;padding:2px 12px;"
            "border-radius:6px;" + colours.get(kind, colours["warning"])
        )
        self.notif.setVisible(True)

    def _hide_notif(self) -> None:
        self.notif.setVisible(False)

    # ── Session history ────────────────────────────────────────────────────

    def _add_history(self, wpm: float, acc: float, err: int, diff: str) -> None:
        self._session_history.insert(0, dict(wpm=wpm, acc=acc, err=err, diff=diff))
        self._session_history = self._session_history[:self.MAX_HISTORY]
        self._refresh_history_ui()

    def _refresh_history_ui(self) -> None:
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._session_history:
            lbl = QLabel("No sessions yet — press  Start  to begin.")
            lbl.setObjectName("histEmpty")
            self.history_layout.addWidget(lbl)
            return

        self.history_layout.addWidget(
            self._hist_row("WPM", "ACCURACY", "ERRORS", "DIFFICULTY", header=True)
        )
        for e in self._session_history:
            self.history_layout.addWidget(
                self._hist_row(str(e["wpm"]), f"{e['acc']}%", str(e["err"]), e["diff"])
            )

    def _hist_row(self, wpm, acc, err, diff, header=False) -> QWidget:
        w   = QWidget()
        w.setObjectName("histHeaderRow" if header else "histRow")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 2, 10, 2); lay.setSpacing(0)
        for text in (wpm, acc, err, diff):
            lbl = QLabel(text)
            lbl.setObjectName("histHeaderCell" if header else "histCell")
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, stretch=1)
        return w

    # ── Session control ────────────────────────────────────────────────────

    @Slot()
    def start_session(self) -> None:
        if not self.target_text:
            self._generate_sentence(self.difficulty_combo.currentText())

        self.timer.duration = self.TIMER_DURATIONS.get(
            self.duration_combo.currentText(), 60
        )
        self.session_active = True
        self.user_input     = ""
        self.input_box.setEnabled(True)
        self.input_box.clear()
        self._sparkline.clear()

        self.engine = TypingEngine(self.target_text)

        if self.stats_tracker is not None:
            try:
                self.stats_tracker.stats_changed.disconnect(self._on_stats_changed)
            except RuntimeError:
                pass
        self.stats_tracker = StatsTracker(self.target_text)
        self.stats_tracker.stats_changed.connect(self._on_stats_changed)

        self._elapsed = 0.0
        self.timer.reset()
        self.timer.start()

        self._hide_notif()
        self.start_btn.setVisible(False)
        self.reset_btn.setEnabled(True)
        self.next_btn.setEnabled(False)
        self.generate_btn.setEnabled(False)
        self.custom_btn.setEnabled(False)
        self.difficulty_combo.setEnabled(False)
        self.duration_combo.setEnabled(False)

        self._refresh_display()
        self._update_expected_key()
        self._update_progress()
        self.keyboard.reset()
        self.input_box.setFocus()
        logger.info("Session started")

    @Slot()
    def reset_session(self) -> None:
        self.session_active = False
        self.timer.stop()
        self.user_input = ""
        self.input_box.clear()
        self.input_box.setEnabled(False)
        self.engine = TypingEngine(self.target_text) if self.target_text else None

        self.start_btn.setVisible(True)
        self.start_btn.setEnabled(True)
        self.reset_btn.setEnabled(False)
        self.next_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.custom_btn.setEnabled(True)
        self.difficulty_combo.setEnabled(True)
        self.duration_combo.setEnabled(True)

        self._refresh_display()
        self._update_expected_key()
        self.progress_bar.setValue(0)
        self._hide_notif()
        self._sparkline.clear()
        self.keyboard.clear_heatmap()

        dur = self.timer.duration
        self.timer_label.setText(f"{dur//60:02d}:{dur%60:02d}")
        self.timer_label.setStyleSheet("")
        self._set_stat(self._wpm_card,  "0")
        self._set_stat(self._acc_card,  "100%")
        self._set_stat(self._err_card,  "0")
        self.keyboard.clear_highlights()
        logger.info("Session reset")

    def _save_session(self, wpm: float, acc: float, err: int, diff: str) -> None:
        try:
            from datetime import datetime

            from typing_trainer.storage.models import KeyStat, TrainingSession
            from typing_trainer.storage.repositories import (
                KeyStatRepository,
                TrainingSessionRepository,
            )

            mode_names = {0: "beginner", 1: "intermediate", 2: "advanced"}
            mode = mode_names.get(self._current_mode, "beginner")

            total = len(self.target_text)
            correct = total - err

            ts = TrainingSession(
                started_at=datetime.now(),
                ended_at=datetime.now(),
                duration_seconds=self._elapsed,
                target_text_hash="",
                difficulty=diff,
                mode=mode,
                wpm=round(wpm, 1),
                accuracy=round(acc, 1),
                errors=err,
                correct=correct,
                xp_earned=max(0, int(wpm * correct / max(total, 1))),
            )
            ts_repo = TrainingSessionRepository()
            saved = ts_repo.create(ts)

            if self.engine:
                error_rates = self.engine.get_error_rate_per_key()
                key_stats = [
                    KeyStat(
                        session_id=saved.id,
                        key_char=key,
                        correct_count=int(total * (100 - rate) / 100) if rate else total,
                        error_count=int(total * rate / 100) if rate else 0,
                        avg_latency_ms=0.0,
                    )
                    for key, rate in error_rates.items()
                ]
                if key_stats:
                    KeyStatRepository().bulk_create(key_stats)
        except Exception as e:
            logger.warning("Failed to save session: %s", e)

    def _session_finished(self) -> None:
        self.session_active = False
        self.timer.stop()
        self.input_box.setEnabled(False)

        self.start_btn.setVisible(True)
        self.start_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.next_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.custom_btn.setEnabled(True)
        self.difficulty_combo.setEnabled(True)
        self.duration_combo.setEnabled(True)

        wpm  = float(self._wpm_card._val.text() or 0)
        acc  = float((self._acc_card._val.text() or "100").replace("%", ""))
        err  = int(self._err_card._val.text() or 0)
        diff = self.difficulty_combo.currentText()
        self._add_history(wpm, acc, err, diff)
        self._save_session(wpm, acc, err, diff)
        self._show_notif(
            f"✓  Done  —  {wpm} WPM  ·  {acc}% accuracy  ·  {err} errors",
            "success"
        )
        logger.info("Session finished: wpm=%.1f acc=%.1f err=%d", wpm, acc, err)

    # ── Timer slots ────────────────────────────────────────────────────────

    @Slot(int)
    def _on_time_updated(self, remaining: int) -> None:
        self.timer_label.setText(f"{remaining//60:02d}:{remaining%60:02d}")
        pct    = remaining / self.timer.duration if self.timer.duration > 0 else 1.0
        colour = "#4ade80" if pct > 0.5 else "#ff9800" if pct > 0.25 else "#ef5350"
        self.timer_label.setStyleSheet(f"color:{colour};")

    @Slot(float)
    def _on_elapsed_updated(self, elapsed: float) -> None:
        self._elapsed = elapsed
        if self.stats_tracker and self.session_active:
            self.stats_tracker.update_time(elapsed)

    @Slot()
    def _on_timer_expired(self) -> None:
        self.timer_label.setText("00:00")
        self.timer_label.setStyleSheet("color:#ef5350;")
        self._show_notif("⏱  Time is up — keep typing to finish the sentence", "danger")

    # ── Typing slots ───────────────────────────────────────────────────────

    @Slot(str)
    def _on_user_input(self, text: str) -> None:
        if not self.session_active:
            return

        # Cap at target length — prevents overtyping
        if len(text) > len(self.target_text):
            self.input_box.blockSignals(True)
            self.input_box.setText(text[:len(self.target_text)])
            self.input_box.blockSignals(False)
            return

        prev_len        = len(self.user_input)
        self.user_input = text
        self._refresh_display()
        if len(text) != prev_len:
            self.keyboard.play_click()

        # Per-keystroke keyboard feedback
        if len(text) > prev_len:
            new_ch   = text[-1]
            expected = self.target_text[prev_len] if prev_len < len(self.target_text) else ""
            if self._current_mode != self.MODE_ADVANCED:
                self.keyboard.handle_feedback(new_ch, new_ch == expected)
        elif len(text) < prev_len:
            self.keyboard.clear_highlights()

        self._update_expected_key()
        self._update_progress()

        if self.stats_tracker:
            self.stats_tracker.update_input(self.user_input)

        if len(self.user_input) >= len(self.target_text):
            self._session_finished()

    @Slot(dict)
    def _on_stats_changed(self, stats: dict) -> None:
        wpm = stats["wpm"]
        self._set_stat(self._wpm_card, str(wpm))
        self._set_stat(self._acc_card, f"{stats['accuracy']}%")
        self._set_stat(self._err_card, str(stats["errors"]))
        self._sparkline.push(wpm)
        if wpm > self._best_wpm:
            self._best_wpm = wpm
            self._set_stat(self._best_card, str(self._best_wpm))

        # Update error heatmap on virtual keyboard
        if "error_rates_per_key" in stats:
            self.keyboard.set_heatmap(stats["error_rates_per_key"])

    # ── Virtual keyboard clicks ────────────────────────────────────────────

    @Slot(str)
    def _on_virtual_key(self, char: str) -> None:
        if not self.session_active:
            return
        if char == "\b":
            self.input_box.setText(self.input_box.text()[:-1])
        elif char not in ("\n", "\t"):
            cur = self.input_box.text()
            if len(cur) < len(self.target_text):
                self.input_box.setText(cur + char)
        self.input_box.setFocus()
