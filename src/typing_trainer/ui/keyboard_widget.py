"""
ui/keyboard_widget.py — Virtual Keyboard Widget
================================================
Builds a full QWERTY keyboard as QPushButton rows.

Public API used by MainWindow
-----------------------------
  set_target(char, next_char, ...)  — highlight expected key
  handle_feedback(char, correct)    — green/red flash
  clear_highlights()                — remove all key highlights
  reset()                           — clear modifiers
  key_pressed  Signal(str)          — emitted when a key button is clicked
  shift_toggled Signal(bool)        — emitted on Shift toggle
"""

from __future__ import annotations

import math
import os
import struct
import tempfile
import wave
from pathlib import Path

from PySide6.QtCore import QPoint, QPointF, QSize, QTimer, QUrl, Signal
try:
    from PySide6.QtMultimedia import QSoundEffect as _QSoundEffect
    _HAS_SOUND = True
except ImportError:
    _QSoundEffect = None  # type: ignore
    _HAS_SOUND = False
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from typing_trainer.ui.mapping import (
    FINGER_BAND,
    GUIDE_BUMP_KEYS,
    HOME_ROW_KEYS,
    KEY_TO_FINGER,
    ROWS,
    SHIFT_MAP,
    UNSHIFT_MAP,
    get_finger,
)

# ── Key display labels ─────────────────────────────────────────────────────────
_DISPLAY: dict[str, str] = {
    "Backspace": "⌫",
    "Tab":       "Tab ⇥",
    "Caps":      "Caps",
    "Enter":     "↵ Enter",
    "LShift":    "⇧ Shift",
    "RShift":    "Shift ⇧",
    "LCtrl":     "Ctrl",
    "RCtrl":     "Ctrl",
    "LAlt":      "Alt",
    "RAlt":      "Alt",
    "LWin":      "❖",
    "RWin":      "❖",
    "Menu":      "☰",
    "Space":     "",
}

# ── Minimum key sizes ──────────────────────────────────────────────────────────
_SIZES: dict[str, QSize] = {
    "Space":     QSize(260, 44),
    "Backspace": QSize(88,  44),
    "Tab":       QSize(76,  44),
    "Caps":      QSize(84,  44),
    "Enter":     QSize(96,  44),
    "LShift":    QSize(112, 44),
    "RShift":    QSize(112, 44),
    "LCtrl":     QSize(62,  44),
    "RCtrl":     QSize(62,  44),
    "LAlt":      QSize(60,  44),
    "RAlt":      QSize(60,  44),
    "LWin":      QSize(52,  44),
    "RWin":      QSize(52,  44),
    "Menu":      QSize(52,  44),
}
_DEFAULT_SIZE = QSize(44, 44)


class VirtualKeyboard(QWidget):
    """Full QWERTY keyboard with animated finger overlay and error heatmap."""

    key_pressed   = Signal(str)
    shift_toggled = Signal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.key_buttons:      dict[str, QPushButton] = {}
        self.modifier_buttons: dict[str, QPushButton] = {}
        self.shift_active = False
        self.caps_lock    = False

        self._highlighted:    set[str]      = set()
        self._feedback_key:   str | None = None
        self._expected_key:   str | None = None
        self._next_key:       str | None = None
        self._shift_hint_key: str | None = None
        self._heatmap_data:   dict[str, float] = {}   # key_id -> error rate (0-100)

        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.setInterval(320)
        self._feedback_timer.timeout.connect(self._clear_feedback)

        self._init_click_sound()
        self._build_rows()

    # ── Layout ─────────────────────────────────────────────────────────────

    def _build_rows(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 6, 8, 8)

        for row_keys in ROWS:
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setSpacing(4)
            row_l.setContentsMargins(0, 0, 0, 0)

            for kid in row_keys:
                btn = self._make_button(kid)
                row_l.addWidget(btn)
                self.key_buttons[kid] = btn
                if len(kid) == 1:
                    self.key_buttons[kid.upper()] = btn
                if kid in ("LShift","RShift","Caps","LCtrl","RCtrl",
                           "LAlt","RAlt","LWin","RWin","Menu",
                           "Enter","Tab","Backspace","Space"):
                    self.modifier_buttons[kid] = btn

            layout.addWidget(row_w)

    # ── Heatmap API ────────────────────────────────────────────────────────

    def set_heatmap(self, error_rates: dict[str, float]) -> None:
        """
        Update error heatmap visualization.
        error_rates: dict mapping key_id (e.g., 'A', 'Space', '1') to error percentage (0-100).
        """
        self._heatmap_data = error_rates or {}
        self._apply_heatmap()

    def _apply_heatmap(self) -> None:
        """Apply heatmap colors to keys based on error rates."""
        for key_id, rate in self._heatmap_data.items():
            btn = self.key_buttons.get(key_id)
            if not btn:
                continue
            # Map 0-100% to a color gradient: green (0%) -> yellow (50%) -> red (100%)
            if rate <= 0:
                btn.setProperty("heatLevel", "none")
            elif rate <= 20:
                btn.setProperty("heatLevel", "low")
            elif rate <= 50:
                btn.setProperty("heatLevel", "medium")
            else:
                btn.setProperty("heatLevel", "high")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def clear_heatmap(self) -> None:
        """Remove all heatmap styling."""
        self._heatmap_data = {}
        for btn in self.key_buttons.values():
            btn.setProperty("heatLevel", "none")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _make_button(self, kid: str) -> QPushButton:
        label = _DISPLAY.get(kid, kid)
        if kid in GUIDE_BUMP_KEYS:
            label = f"{kid}▪"

        btn = QPushButton(label)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setMinimumSize(_SIZES.get(kid, _DEFAULT_SIZE))
        btn.setProperty("keyId",    kid)
        btn.setProperty("keyState", "")

        if kid.upper() in HOME_ROW_KEYS:
            btn.setProperty("homeRow", "true")

        uk     = kid.upper()
        finger = KEY_TO_FINGER.get(uk, KEY_TO_FINGER.get(kid, ""))
        if finger:
            band = FINGER_BAND.get(finger, "")
            if band:
                btn.setProperty("fingerBand", band)

        btn.clicked.connect(self._on_btn_clicked)
        return btn

    # ── Click sound ────────────────────────────────────────────────────────

    def _generate_click_wav(self) -> bytes:
        sample_rate = 22050
        duration = 0.04
        num_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            envelope = math.exp(-t * 100)
            value = int((math.sin(2 * math.pi * 1200 * t) * 0.6 +
                         math.sin(2 * math.pi * 2400 * t) * 0.4) * envelope * 32767 * 0.25)
            value = max(-32768, min(32767, value))
            buf.extend(struct.pack('<h', value))
        return bytes(buf)

    def _init_click_sound(self) -> None:
        self._click_sound = None
        try:
            wav_path = Path(tempfile.gettempdir()) / "typing_trainer_click.wav"
            if not wav_path.exists():
                wav_data = self._generate_click_wav()
                with wave.open(str(wav_path), 'w') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(22050)
                    wf.writeframes(wav_data)
            self._click_sound = _QSoundEffect(self)
            self._click_sound.setSource(QUrl.fromLocalFile(str(wav_path)))
            self._click_sound.setVolume(0.4)
        except Exception:
            pass

    def play_click(self) -> None:
        if self._click_sound and not self._click_sound.isPlaying():
            self._click_sound.play()

    # ── Coordinate query ───────────────────────────────────────────────────

    def get_key_center(self, key_id: str) -> QPointF | None:
        """Return key centre in this widget's local coordinate space."""
        btn = self.key_buttons.get(key_id)
        if btn is None:
            return None
        mapped: QPoint = btn.mapTo(self, btn.rect().center())
        return QPointF(mapped)

    # ── Public API ─────────────────────────────────────────────────────────

    def set_target(self, char: str | None,
                   next_char: str | None = None,
                   show_highlights: bool = True) -> None:
        self._clear_expected()

        if not char:
            return

        self._expected_key   = self._char_to_btn_id(char)
        self._next_key       = self._char_to_btn_id(next_char) if next_char else None
        self._shift_hint_key = None

        needs_shift = (char.isupper() and char.isalpha()) or (char in SHIFT_MAP.values())
        if needs_shift and self._expected_key:
            finger, _ = get_finger(char)
            self._shift_hint_key = "LShift" if (finger and "Right" in finger) else "RShift"

        if show_highlights:
            self._apply_highlights()

    def handle_feedback(self, char: str, correct: bool) -> None:
        """Flash key green (correct) or red (incorrect)."""
        key_id = self._char_to_btn_id(char)
        if key_id and key_id in self.key_buttons:
            self._set_state(key_id, "correct" if correct else "incorrect")
            self._feedback_key = key_id
            self._highlighted.add(key_id)
            self._feedback_timer.start()

    def clear_highlights(self) -> None:
        for kid in list(self._highlighted):
            self._set_state(kid, "")
        self._highlighted.clear()
        self._feedback_key   = None
        self._expected_key   = None
        self._next_key       = None
        self._shift_hint_key = None

    def reset(self) -> None:
        self.shift_active = False
        self.caps_lock    = False
        for btn in self.modifier_buttons.values():
            btn.setProperty("modState", "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.clear_highlights()

    # ── Internals ──────────────────────────────────────────────────────────

    def _char_to_btn_id(self, char: str) -> str | None:
        if not char:
            return None
        if char == " ":
            return "Space"
        upper = char.upper()
        if upper in self.key_buttons:
            return upper
        base = UNSHIFT_MAP.get(char)
        if base:
            bid = base.upper() if base.isalpha() else base
            if bid in self.key_buttons:
                return bid
        return None

    def _clear_expected(self) -> None:
        for kid in list(self._highlighted):
            if kid != self._feedback_key:
                self._set_state(kid, "")
        self._highlighted = {self._feedback_key} if self._feedback_key else set()

    def _apply_highlights(self) -> None:
        for kid, state in (
            (self._expected_key,   "expected"),
            (self._next_key,       "next"),
            (self._shift_hint_key, "shift_hint"),
        ):
            if kid and kid in self.key_buttons:
                self._set_state(kid, state)
                self._highlighted.add(kid)

    def _set_state(self, key_id: str, state: str) -> None:
        btn = self.key_buttons.get(key_id)
        if btn:
            btn.setProperty("keyState", state)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _clear_feedback(self) -> None:
        if not self._feedback_key:
            return
        kid = self._feedback_key
        self._feedback_key = None
        if   kid == self._expected_key:   self._set_state(kid, "expected")
        elif kid == self._next_key:        self._set_state(kid, "next")
        elif kid == self._shift_hint_key:  self._set_state(kid, "shift_hint")
        else:
            self._set_state(kid, "")
            self._highlighted.discard(kid)

    def _on_btn_clicked(self) -> None:
        btn = self.sender()
        if not btn:
            return
        kid: str = btn.property("keyId")
        if not kid:
            return

        self.play_click()

        if kid in ("LShift", "RShift"):
            self.shift_active = not self.shift_active
            self.shift_toggled.emit(self.shift_active)
            btn.setProperty("modState", "active" if self.shift_active else "")
            btn.style().unpolish(btn); btn.style().polish(btn)
            return

        if kid == "Caps":
            self.caps_lock = not self.caps_lock
            btn.setProperty("modState", "active" if self.caps_lock else "")
            btn.style().unpolish(btn); btn.style().polish(btn)
            return

        char = self._key_id_to_char(kid)
        if char is not None:
            self.key_pressed.emit(char)

        # Auto-release Shift after one key
        if self.shift_active:
            self.shift_active = False
            self.shift_toggled.emit(False)
            for sid in ("LShift", "RShift"):
                sb = self.modifier_buttons.get(sid)
                if sb:
                    sb.setProperty("modState", "")
                    sb.style().unpolish(sb)
                    sb.style().polish(sb)

    def _key_id_to_char(self, kid: str) -> str | None:
        if kid == "Space":     return " "
        if kid == "Backspace": return "\b"
        if kid == "Enter":     return "\n"
        if kid == "Tab":       return "\t"
        if len(kid) == 1:
            upper_mode = self.shift_active != self.caps_lock
            if kid.isalpha():
                return kid.upper() if upper_mode else kid.lower()
            return SHIFT_MAP.get(kid, kid) if self.shift_active else kid
        return None
