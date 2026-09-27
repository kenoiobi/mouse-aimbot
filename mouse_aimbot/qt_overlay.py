"""
PyQt6 snap engine + optional click-through debug overlay.

Overlay pattern adapted from TargetFinder Toolkit (MIT):
https://github.com/ahmedbenakouche/target_finder_toolkit
"""

from __future__ import annotations

import logging
import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from mouse_aimbot.config import Config, DEFAULT
from mouse_aimbot.inference import Detection, detections_from_targetfinder
from mouse_aimbot.magnetic import compute_snap

log = logging.getLogger("mouse-aimbot")


class SnapEngine(QtCore.QObject):
    """Magnetic snap loop with no window (no taskbar / focus side effects)."""

    def __init__(self, detector, config: Config = DEFAULT, parent=None) -> None:
        super().__init__(parent)
        self.detector = detector
        self.config = config
        self._prev_pos: tuple[float, float] | None = None
        self._snapped: Detection | None = None
        self._snap_enabled = True
        self._alive = True

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(config.overlay_tick_ms)

    @property
    def snapped(self) -> Detection | None:
        return self._snapped

    def shutdown(self) -> None:
        self._alive = False
        self._snap_enabled = False
        if self._timer.isActive():
            self._timer.stop()

    def _tick(self) -> None:
        if not self._alive or not self._snap_enabled:
            return
        detections = detections_from_targetfinder(self.detector.get_detections())
        self._apply_snap(detections)

    def _apply_snap(self, detections: list[Detection]) -> None:
        # Qt read+write keeps logical coords aligned with TargetFinder boxes.
        pos = QtGui.QCursor.pos()
        raw_x, raw_y = float(pos.x()), float(pos.y())
        result = compute_snap(
            raw_x,
            raw_y,
            detections,
            prev_pos=self._prev_pos,
            config=self.config,
        )
        self._prev_pos = (raw_x, raw_y)
        self._snapped = result.target if result.snapped else None

        fx, fy = int(round(result.x)), int(round(result.y))
        if fx != int(raw_x) or fy != int(raw_y):
            QtGui.QCursor.setPos(fx, fy)


class SnapOverlay(QtWidgets.QWidget):
    """Transparent, input-through overlay that paints detections (debug)."""

    def __init__(
        self,
        detector,
        config: Config = DEFAULT,
        engine: SnapEngine | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.detector = detector
        self.config = config
        self.engine = engine
        self._alive = True

        screen = QtWidgets.QApplication.primaryScreen()
        if screen is not None:
            self.detector.overlay_window[str(screen.name())] = self
            geom = screen.geometry()
        else:
            geom = QtCore.QRect(0, 0, 800, 600)
        self.screen_geometry = geom
        self.setGeometry(geom)

        flags = (
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.WindowTransparentForInput
            | QtCore.Qt.WindowType.WindowDoesNotAcceptFocus
        )
        if sys.platform != "darwin":
            flags |= QtCore.Qt.WindowType.Tool
        if sys.platform.startswith("linux"):
            flags |= QtCore.Qt.WindowType.X11BypassWindowManagerHint

        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.active = True

        # Repaint only — snap runs on SnapEngine. Avoids coupling paint to hide/show.
        self._paint_timer = QtCore.QTimer(self)
        self._paint_timer.timeout.connect(self.update)
        self._paint_timer.start(max(16, config.overlay_tick_ms))

    def activate(self) -> None:
        self.active = True

    def reset(self) -> None:
        self.active = False
        self.update()

    def hide(self) -> None:  # noqa: A003
        """
        TargetFinder may call hide() before capture. Do not actually hide the
        HWND — that flashes the Windows taskbar. Just stop painting.
        """
        self.active = False
        self.update()

    def show(self) -> None:  # noqa: A003
        """Pair with hide(): resume painting; only map the window once."""
        if not self._alive:
            return
        self.active = True
        if not self.isVisible():
            super().show()
        self.update()

    def shutdown(self) -> None:
        self._alive = False
        self.active = False
        if self._paint_timer.isActive():
            self._paint_timer.stop()
        for key, ov in list(getattr(self.detector, "overlay_window", {}).items()):
            if ov is self:
                self.detector.overlay_window.pop(key, None)
        # Real hide/close for teardown (bypass our no-flash hide()).
        QtWidgets.QWidget.hide(self)
        self.close()
        self.deleteLater()

    def paintEvent(self, event) -> None:  # noqa: N802
        if not self._alive or not self.active or not self.config.overlay_enabled:
            return

        detections = detections_from_targetfinder(self.detector.get_detections())
        if not detections:
            return

        snapped = self.engine.snapped if self.engine is not None else None
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        cand = QtGui.QColor(*self.config.overlay_candidate_rgb, 220)
        snap = QtGui.QColor(*self.config.overlay_snapped_rgb, 240)

        for det in detections:
            x1, y1, x2, y2 = det.bbox
            is_snapped = snapped is not None and (
                abs(det.center[0] - snapped.center[0]) < 0.5
                and abs(det.center[1] - snapped.center[1]) < 0.5
            )
            color = snap if is_snapped else cand
            width = (
                self.config.overlay_snapped_line_width
                if is_snapped
                else self.config.overlay_line_width
            )
            painter.setPen(QtGui.QPen(color, width))
            painter.drawRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))

            label = f"{det.class_name} {det.confidence:.2f}"
            fm = painter.fontMetrics()
            tw, th = fm.horizontalAdvance(label), fm.height()
            painter.fillRect(
                int(x1), int(y1) - th, tw + 4, th, QtGui.QColor(0, 0, 0, 120)
            )
            painter.drawText(int(x1) + 2, int(y1) - 2, label)

        painter.end()
