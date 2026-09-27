"""OS cursor read / inject — platform factory."""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod


class CursorController(ABC):
    @abstractmethod
    def get_position(self) -> tuple[int, int]:
        ...

    @abstractmethod
    def set_position(self, x: int, y: int) -> None:
        ...


def get_cursor_controller() -> CursorController:
    if sys.platform == "win32":
        from kill_mouse.platform.windows.cursor import WindowsCursorController

        return WindowsCursorController()
    if sys.platform == "darwin":
        from kill_mouse.platform.macos.cursor import MacOSCursorController

        return MacOSCursorController()
    if sys.platform.startswith("linux"):
        from kill_mouse.platform.linux.cursor import LinuxCursorController

        return LinuxCursorController()
    raise NotImplementedError(f"Unsupported platform: {sys.platform}")
