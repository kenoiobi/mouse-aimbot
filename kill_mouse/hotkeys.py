"""Force-quit hotkey listener."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable

from kill_mouse.config import DEFAULT

log = logging.getLogger("kill-mouse")


class QuitHotkey:
    """Always-on listener; Ctrl+Alt+Q (configurable) stops the daemon."""

    def __init__(self, on_quit: Callable[[], None], hotkey: str = DEFAULT.quit_hotkey) -> None:
        self._on_quit = on_quit
        self._hotkey = hotkey
        self._listener = None
        self._fired = threading.Event()

    def start(self) -> None:
        from pynput import keyboard

        def _fire() -> None:
            if self._fired.is_set():
                return
            self._fired.set()
            # Do not do Qt/teardown work on the pynput thread.
            threading.Thread(target=self._on_quit, name="quit-hotkey", daemon=True).start()

        self._listener = keyboard.GlobalHotKeys({self._hotkey: _fire})
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        listener = self._listener
        self._listener = None
        if listener is None:
            return
        try:
            listener.stop()
        except Exception:
            log.exception("Failed to stop hotkey listener")
        # Never block forever — this is what froze the terminal before.
        try:
            listener.join(timeout=1.0)
        except Exception:
            pass
