"""
mouse-aimbot application entrypoint.

Uses TargetFinder Toolkit for UI-widget detection + PyQt overlay, and our
magnetic snap to warp the cursor toward nearby targets.
"""

from __future__ import annotations

import logging
import sys

from mouse_aimbot.config import DEFAULT, Config
from mouse_aimbot.hotkeys import QuitHotkey

log = logging.getLogger("mouse-aimbot")


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    from dataclasses import replace

    config: Config = DEFAULT
    if "--no-overlay" in argv:
        config = replace(DEFAULT, overlay_enabled=False)

    from PyQt6 import QtCore, QtWidgets
    from target_finder_toolkit.targetfinder import TargetFinder

    from mouse_aimbot.qt_overlay import SnapEngine, SnapOverlay

    mode = "debug overlay" if config.overlay_enabled else "no overlay"
    log.info("Starting mouse-aimbot (%s + magnetic snap)", mode)
    log.info("Force quit: %s", config.quit_hotkey)

    qt_app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    # Headless (no overlay window) must not quit when zero windows are open.
    qt_app.setQuitOnLastWindowClosed(config.overlay_enabled)

    log.info("Loading TargetFinder model %s …", config.model_name)
    detector = TargetFinder(
        model_name=config.model_name,
        change_thresh=config.change_thresh,
        capture_interval=config.capture_interval_s,
        confidence=config.conf_threshold,
        iou=config.iou_threshold,
    )
    # Hide/show of the overlay HWND flashes the Windows taskbar. We skip paint
    # via SnapOverlay.hide()/show() overrides instead when capture needs it.
    detector.hide_overlay_during_capture = False
    log.info("Model ready")

    engine = SnapEngine(detector, config)
    overlay: SnapOverlay | None = None

    if config.overlay_enabled:
        # TODO(multi-monitor): one SnapOverlay per QScreen.
        overlay = SnapOverlay(detector, config, engine=engine)
        screen = QtWidgets.QApplication.primaryScreen()
        if screen is not None:
            g = screen.geometry()
            overlay.setGeometry(g)
            overlay.move(g.x(), g.y())
        overlay.show()  # uses WA_ShowWithoutActivating — no raise_/activate

    detector.start()

    state = {"done": False}

    class _QuitBridge(QtCore.QObject):
        requested = QtCore.pyqtSignal()

    bridge = _QuitBridge()

    def _shutdown() -> None:
        if state["done"]:
            return
        state["done"] = True
        log.info("Shutting down…")
        try:
            engine.shutdown()
        except Exception:
            log.exception("Engine shutdown failed")
        if overlay is not None:
            try:
                overlay.shutdown()
            except Exception:
                log.exception("Overlay shutdown failed")
        try:
            detector.stop()
        except Exception:
            log.exception("Detector stop failed")
        try:
            hotkey.stop()
        except Exception:
            log.exception("Hotkey stop failed")
        qt_app.quit()

    bridge.requested.connect(_shutdown)

    def _quit_from_hotkey() -> None:
        log.info("Quit requested (%s)", config.quit_hotkey)
        bridge.requested.emit()

    hotkey = QuitHotkey(_quit_from_hotkey, config.quit_hotkey)
    hotkey.start()

    code = qt_app.exec()
    if not state["done"]:
        _shutdown()
    log.info("Stopped")
    raise SystemExit(code)


if __name__ == "__main__":
    main()
