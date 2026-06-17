"""
ui/finger_widget.py — Hand Illustration Overlay  v4  (Image-1 style)
=====================================================================
Fixes
-----
  VISUAL   — proper separated fingers with inter-finger gaps, correctly
             proportioned to the *actual* rendered key width so the hands
             look right at any window size.  Palm is a clean oval shape,
             NOT a wide boat.  Fingers are open-bottomed capsules drawn on
             top of the palm, producing natural skin-tone gaps between them.

  FUNCTIONAL — animate_to_key works for ALL keyboard rows.  The active
             finger's tip slides from its home-key to the *target* key
             (computing the real pixel offset), stays briefly, then returns.
             Upper rows, lower rows, same-row off-home keys all work.

Public API (unchanged)
----------------------
  animate_to_key(char)     highlight + animate the correct finger
  set_active_finger(name)  force-highlight by finger name
  set_visible_mode(bool)   show / hide overlay
  reset_all()              clear all state
  refresh_positions()      call after keyboard resize
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Optional, Tuple

from PySide6.QtCore import (
    Qt, QObject, QPointF, QRectF, QTimer,
    Property, QPropertyAnimation,
    QSequentialAnimationGroup, QPauseAnimation,
    QAbstractAnimation, QEasingCurve,
)
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPainterPath,
    QLinearGradient, QRadialGradient,
)

from typing_trainer.ui.mapping import KEY_TO_FINGER, HOME_KEYS, UNSHIFT_MAP

if TYPE_CHECKING:
    from typing_trainer.ui.keyboard_widget import VirtualKeyboard

# ── Finger-to-key assignment ───────────────────────────────────────────────────
_LEFT_KEYS   = ["A", "S", "D", "F"]
_LEFT_NAMES  = ["Left Pinky", "Left Ring", "Left Middle", "Left Index"]

_RIGHT_KEYS  = ["J", "K", "L", ";"]
_RIGHT_NAMES = ["Right Index", "Right Middle", "Right Ring", "Right Pinky"]

# Natural finger-length ratios (multiple of key height).
# Middle is longest, pinky is shortest — matches anatomy.
_LEFT_RATIOS  = [1.00, 1.25, 1.40, 1.20]   # pinky → index
_RIGHT_RATIOS = [1.20, 1.40, 1.25, 1.00]   # index → pinky

# Widths as fractions of the key-to-key spacing
_FW_FRAC    = 0.30    # regular finger
_THUMB_FRAC = 0.34    # thumb (a bit wider)

# Press/reach animation depth (px; also used for home-row press feel)
_PRESS_DEPTH = 7

# ── Palette ────────────────────────────────────────────────────────────────────
_SKIN      = QColor(230, 218, 200, 185)
_SKIN_MID  = QColor(215, 203, 182, 182)
_SKIN_DARK = QColor(195, 182, 160, 178)
_OUTLINE   = QColor( 48,  38,  26, 230)

_ACT_FILL    = QColor( 55, 210,  65, 245)   # vivid green (Image-1 style)
_ACT_OUTLINE = QColor( 12, 138,  18, 255)
_ACT_GLOW    = QColor( 55, 210,  65,  48)


# ─────────────────────────────────────────────────────────────────────────────
#  _AnimFloat — minimal animatable float Qt property
# ─────────────────────────────────────────────────────────────────────────────

class _AnimFloat(QObject):
    def __init__(self, notify_fn, parent=None):
        super().__init__(parent)
        self._v      = 0.0
        self._notify = notify_fn

    def _get(self):      return self._v
    def _set(self, v):
        self._v = v
        self._notify()

    value = Property(float, _get, _set)


# ─────────────────────────────────────────────────────────────────────────────
#  FingerOverlay
# ─────────────────────────────────────────────────────────────────────────────

class FingerOverlay(QWidget):
    """
    Transparent overlay drawn on top of VirtualKeyboard.
    Renders two anatomical hand illustrations whose active finger reaches to
    the correct key for any row (number row, QWERTY, home, bottom, space).
    """

    def __init__(self, keyboard: "VirtualKeyboard", parent=None) -> None:
        super().__init__(parent)
        self.keyboard = keyboard
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setVisible(True)

        self._visible_mode   = True
        self._active_finger: Optional[str] = None

        # Reach offset: (target_key_center − home_key_center), in pixels.
        # Animated with _press._v so both reach and press share one timeline.
        self._reach: Tuple[float, float] = (0.0, 0.0)

        # Progress value: 0 = rest, 1 = fully at target, then back to 0
        self._press = _AnimFloat(self.update, parent=self)
        self._seq:   Optional[QSequentialAnimationGroup] = None

        # API compatibility shim
        self.fingers: dict = {}

        QTimer.singleShot(80, self.update)

    # ── Public API ─────────────────────────────────────────────────────────

    def set_visible_mode(self, visible: bool) -> None:
        self._visible_mode = visible
        self.update()

    def set_active_finger(self, finger_name: Optional[str]) -> None:
        self._active_finger = finger_name
        self.update()

    def animate_to_key(self, char: str) -> None:
        """Identify the right finger, compute reach offset, play animation."""
        key_id = self._resolve_key_id(char)
        if not key_id:
            return
        finger = KEY_TO_FINGER.get(key_id.upper(), KEY_TO_FINGER.get(key_id, ""))
        if char == " ":
            finger = "Left Thumb"
        if not finger:
            return

        # --- compute reach offset -----------------------------------------
        home_key = HOME_KEYS.get(finger, "")
        home_c   = self.keyboard.get_key_center(home_key) if home_key else None
        tgt_c    = self.keyboard.get_key_center(key_id)

        if home_c and tgt_c:
            self._reach = (tgt_c.x() - home_c.x(),
                           tgt_c.y() - home_c.y())
        else:
            self._reach = (0.0, _PRESS_DEPTH)   # tiny home-row press feel

        self._active_finger = finger
        self._play_press()

    def reset_all(self) -> None:
        self._active_finger = None
        self._reach = (0.0, 0.0)
        if self._seq:
            self._seq.stop()
            self._seq = None
        self._press._v = 0.0
        self.update()

    def refresh_positions(self) -> None:
        QTimer.singleShot(30, self.update)

    # ── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_key_id(char: str) -> Optional[str]:
        if not char:
            return None
        if char == " ":
            return "Space"
        upper = char.upper()
        if upper in KEY_TO_FINGER:
            return upper
        base = UNSHIFT_MAP.get(char)
        if base:
            return base.upper() if base.isalpha() else base
        return None

    def _play_press(self) -> None:
        if self._seq:
            self._seq.stop()
        self._press._v = 0.0

        def _mk(s, e, ms, ease=QEasingCurve.Type.OutCubic):
            a = QPropertyAnimation(self._press, b"value", self)
            a.setDuration(ms)
            a.setStartValue(float(s))
            a.setEndValue(float(e))
            a.setEasingCurve(ease)
            return a

        seq = QSequentialAnimationGroup(self)
        seq.addAnimation(_mk(0.0, 1.0, 175))
        seq.addAnimation(QPauseAnimation(110, self))
        seq.addAnimation(_mk(1.0, 0.0, 215, QEasingCurve.Type.InOutCubic))

        def _done():
            self._active_finger = None
            self._reach = (0.0, 0.0)
            self.update()

        seq.finished.connect(_done)
        seq.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        self._seq = seq

    # ── Dimension computation (adapts to actual key size at any window) ────

    def _dims(self):
        """(key_spacing, key_h, fw, thumb_w, left_lengths, right_lengths)"""
        pa = self.keyboard.get_key_center("A")
        ps = self.keyboard.get_key_center("S")
        key_sp = (ps.x() - pa.x()) if (pa and ps) else 52.0

        btn    = self.keyboard.key_buttons.get("A")
        key_h  = float(btn.height()) if btn else 44.0

        fw      = max(13.0, min(36.0, key_sp * _FW_FRAC))
        thumb_w = max(15.0, min(42.0, key_sp * _THUMB_FRAC))

        ll = [key_h * r for r in _LEFT_RATIOS]
        rl = [key_h * r for r in _RIGHT_RATIOS]
        return key_sp, key_h, fw, thumb_w, ll, rl

    # ── Paint entry ────────────────────────────────────────────────────────

    def paintEvent(self, _event) -> None:
        if not self._visible_mode:
            return
        key_sp, key_h, fw, thumb_w, ll, rl = self._dims()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        self._draw_hand(p, _LEFT_KEYS,  _LEFT_NAMES,  ll, "left",  fw, thumb_w, key_h)
        self._draw_hand(p, _RIGHT_KEYS, _RIGHT_NAMES, rl, "right", fw, thumb_w, key_h)
        p.end()

    # ══════════════════════════════════════════════════════════════════════
    #  HAND DRAWING
    # ══════════════════════════════════════════════════════════════════════

    def _draw_hand(self, p: QPainter,
                   keys:    List[str],
                   names:   List[str],
                   lengths: List[float],
                   side:    str,
                   fw:      float,
                   thumb_w: float,
                   key_h:   float) -> None:

        # --- Gather home-row positions ---
        home_pts: List[Optional[Tuple[float, float]]] = []
        for k in keys:
            c = self.keyboard.get_key_center(k)
            home_pts.append((c.x(), c.y()) if c else None)
        if any(t is None for t in home_pts):
            return
        space_c = self.keyboard.get_key_center("Space")
        if space_c is None:
            return

        # Animation factor  0→1→0
        factor = math.sin(self._press._v * math.pi)
        rdx, rdy = self._reach

        # --- Compute animated tip + base per finger ---
        # Tip = where the fingertip is RIGHT NOW (home or reaching to target)
        # Base = below the tip by the finger's natural length; moves 40% of
        #        the tip's reach so the finger appears to tilt/stretch.
        tips:  List[Tuple[float, float]] = []
        bases: List[Tuple[float, float]] = []
        for (hx, hy), name, length in zip(home_pts, names, lengths):
            if name == self._active_finger:
                tx = hx + rdx * factor
                ty = hy + rdy * factor
                bx = hx + rdx * factor * 0.38
                by = hy + rdy * factor * 0.38 + length
            else:
                tx, ty = float(hx), float(hy)
                bx, by = float(hx), float(hy) + length
            tips.append((tx, ty))
            bases.append((bx, by))

        # Thumb
        thumb_name = "Left Thumb" if side == "left" else "Right Thumb"
        if side == "left":
            th_ax = home_pts[-1][0] + fw * 1.2      # anchor near index-palm
            th_ay = max(b[1] for b in bases) + key_h * 0.30
            th_tx = space_c.x() - key_h * 1.2
        else:
            th_ax = home_pts[0][0]  - fw * 1.2
            th_ay = max(b[1] for b in bases) + key_h * 0.30
            th_tx = space_c.x() + key_h * 1.2
        th_ty = space_c.y()
        if thumb_name == self._active_finger:
            th_tx += rdx * factor
            th_ty += rdy * factor

        # Palm geometry (fixed to home-row positions, NOT animated)
        home_xs = [p[0] for p in home_pts]
        palm_x0 = min(home_xs) - fw * 0.60
        palm_x1 = max(home_xs) + fw * 0.60
        palm_top = max(hy + l for (hx, hy), l in zip(home_pts, lengths))
        palm_bot = palm_top + key_h * 1.05
        wrist_y  = palm_bot + key_h * 0.70
        wi = (palm_x1 - palm_x0) * 0.17

        # ── 1. Palm + wrist (drawn first, behind everything) ────────────
        self._draw_palm(p, palm_x0, palm_x1, palm_top, palm_bot,
                        wi, wrist_y)

        # ── 2. Thumb ────────────────────────────────────────────────────
        self._draw_thumb(p, th_ax, th_ay, th_tx, th_ty,
                         thumb_w, thumb_name)

        # ── 3. Fingers (open-bottomed capsules on top of palm) ──────────
        for (tx, ty), (bx, by), name in zip(tips, bases, names):
            self._draw_finger(p, tx, ty, bx, by, fw, name)

    # ── Palm ───────────────────────────────────────────────────────────────

    def _draw_palm(self, p: QPainter,
                   x0, x1, top, bot, wi, wrist_y) -> None:
        """Flat-top palm block tapering to a wrist."""
        path = QPainterPath()
        path.moveTo(x0, top)
        path.lineTo(x1, top)
        # Right side curves to wrist
        path.cubicTo(x1 + 8, bot,
                     x1 - wi + 6, bot,
                     x1 - wi, wrist_y)
        # Wrist bottom
        path.lineTo(x0 + wi, wrist_y)
        # Left side back up
        path.cubicTo(x0 + wi - 6, bot,
                     x0 - 8, bot,
                     x0, top)
        path.closeSubpath()

        grad = QLinearGradient(0.0, top, 0.0, wrist_y)
        grad.setColorAt(0.0, _SKIN)
        grad.setColorAt(0.55, _SKIN_MID)
        grad.setColorAt(1.0, _SKIN_DARK)
        p.setBrush(QBrush(grad))
        p.setPen(QPen(_OUTLINE, 1.8))
        p.drawPath(path)

    # ── Single finger ──────────────────────────────────────────────────────

    def _draw_finger(self, p: QPainter,
                     tx: float, ty: float,
                     bx: float, by: float,
                     fw: float, name: str) -> None:
        """
        Open-bottomed capsule: left side + fingertip arc + right side.
        No closing line at the base so it blends seamlessly into the palm.
        The finger has a natural taper (narrower at tip, wider at base).
        """
        active = (name == self._active_finger)
        hw     = fw / 2.0
        hw_tip = hw * 0.75          # slightly narrower at the very tip
        fh     = by - ty

        # Soft glow for the active finger
        if active:
            glow = QRadialGradient(QPointF(tx, ty + fh * 0.35), hw * 3.8)
            glow.setColorAt(0.0, _ACT_GLOW)
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(glow))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(tx, ty + fh * 0.35), hw * 3.8, fh * 0.65)

        # Open-bottomed capsule path (NO close at base)
        path = QPainterPath()
        #   start at bottom-left
        path.moveTo(bx - hw, by)
        #   up left side with slight inward taper
        path.cubicTo(bx - hw, by - fh * 0.25,
                     tx - hw_tip, ty + hw_tip * 1.1,
                     tx - hw_tip, ty + hw_tip)
        #   arc over the fingertip
        path.quadTo(tx - hw_tip, ty,  tx,         ty)
        path.quadTo(tx + hw_tip, ty,  tx + hw_tip, ty + hw_tip)
        #   down right side (mirror of left)
        path.cubicTo(tx + hw_tip, ty + hw_tip * 1.1,
                     bx + hw,     by - fh * 0.25,
                     bx + hw,     by)
        # deliberately NOT closing — open at the base

        # Fill
        if active:
            c1 = QColor(_ACT_FILL); c1.setAlpha(248)
            c2 = QColor(_ACT_FILL).lighter(120); c2.setAlpha(248)
            grad = QLinearGradient(tx - hw, ty, tx + hw, ty)
            grad.setColorAt(0.0, c2); grad.setColorAt(0.5, c1); grad.setColorAt(1.0, c2)
            fill   = QBrush(grad)
            border = QPen(_ACT_OUTLINE, 2.1)
        else:
            c1 = QColor(242, 232, 215, 190)
            c2 = QColor(215, 203, 182, 182)
            grad = QLinearGradient(tx - hw, ty, tx + hw, ty)
            grad.setColorAt(0.0, c2); grad.setColorAt(0.45, c1); grad.setColorAt(1.0, c2)
            fill   = QBrush(grad)
            border = QPen(_OUTLINE, 1.7)

        p.setBrush(fill)
        p.setPen(border)
        p.drawPath(path)

        # Knuckle creases  (2 faint horizontal lines)
        p.setOpacity(0.30 if not active else 0.46)
        p.setPen(QPen(_ACT_OUTLINE if active else _OUTLINE, 0.9))
        for frac in (0.33, 0.60):
            ky = ty + fh * frac
            p.drawLine(QPointF(tx - hw + 3, ky), QPointF(tx + hw - 3, ky))
        p.setOpacity(1.0)

        # Fingernail highlight near tip
        p.setBrush(QBrush(QColor(255, 255, 255, 118 if active else 90)))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(tx, ty + fh * 0.11), hw * 0.50, fh * 0.085)

    # ── Thumb ──────────────────────────────────────────────────────────────

    def _draw_thumb(self, p: QPainter,
                    ax: float, ay: float,   # anchor (palm side)
                    tx: float, ty: float,   # tip (space bar side)
                    thumb_w: float,
                    name:    str) -> None:
        """Tilted capsule for the thumb."""
        active = (name == self._active_finger)
        thw    = thumb_w / 2.0

        dx, dy = tx - ax, ty - ay
        dist   = math.hypot(dx, dy)
        if dist < 2:
            return
        ux, uy = dx / dist, dy / dist
        nx, ny = -uy,  ux

        # Glow
        if active:
            glow = QRadialGradient(QPointF(tx, ty), thw * 3.5)
            glow.setColorAt(0.0, _ACT_GLOW)
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(glow))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(tx, ty), thw * 3.5, thw * 3.0)

        # Capsule
        path = QPainterPath()
        path.moveTo(tx    + nx * thw, ty    + ny * thw)
        path.quadTo(tx    + ux * thw, ty    + uy * thw,
                    tx    - nx * thw, ty    - ny * thw)
        path.lineTo(ax    - nx * thw, ay    - ny * thw)
        path.quadTo(ax    - ux * thw, ay    - uy * thw,
                    ax    + nx * thw, ay    + ny * thw)
        path.closeSubpath()

        if active:
            p.setBrush(QBrush(_ACT_FILL))
            p.setPen(QPen(_ACT_OUTLINE, 2.1))
        else:
            grad = QLinearGradient(QPointF(ax, ay), QPointF(tx, ty))
            grad.setColorAt(0.0, _SKIN_DARK)
            grad.setColorAt(1.0, _SKIN)
            p.setBrush(QBrush(grad))
            p.setPen(QPen(_OUTLINE, 1.7))

        p.drawPath(path)

        # Knuckle crease on thumb
        mid_x = (tx + ax) / 2
        mid_y = (ty + ay) / 2
        p.setOpacity(0.28 if not active else 0.44)
        p.setPen(QPen(_ACT_OUTLINE if active else _OUTLINE, 0.9))
        p.drawLine(QPointF(mid_x + nx * (thw - 3), mid_y + ny * (thw - 3)),
                   QPointF(mid_x - nx * (thw - 3), mid_y - ny * (thw - 3)))
        p.setOpacity(1.0)
