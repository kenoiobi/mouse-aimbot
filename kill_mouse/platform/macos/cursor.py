"""macOS cursor stub."""

from __future__ import annotations

from kill_mouse.cursor import CursorController


class MacOSCursorController(CursorController):
    def get_position(self) -> tuple[int, int]:
        raise NotImplementedError(
            "macOS cursor integration not implemented yet. "
            "Use CGEventSource / Quartz for get, CGWarpMouseCursorPosition for set."
        )

    def set_position(self, x: int, y: int) -> None:
        raise NotImplementedError(
            "macOS cursor integration not implemented yet. "
            "Use CGWarpMouseCursorPosition / CGEventCreateMouseEvent."
        )
