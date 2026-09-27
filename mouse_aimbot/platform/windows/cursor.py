"""Windows cursor via win32api."""

from __future__ import annotations

import win32api

from mouse_aimbot.cursor import CursorController


class WindowsCursorController(CursorController):
    def get_position(self) -> tuple[int, int]:
        x, y = win32api.GetCursorPos()
        return int(x), int(y)

    def set_position(self, x: int, y: int) -> None:
        win32api.SetCursorPos((int(x), int(y)))
