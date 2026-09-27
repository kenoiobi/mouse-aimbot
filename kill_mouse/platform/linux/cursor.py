"""Linux cursor stub (X11 / Wayland)."""

from __future__ import annotations

from kill_mouse.cursor import CursorController


class LinuxCursorController(CursorController):
    def get_position(self) -> tuple[int, int]:
        raise NotImplementedError(
            "Linux cursor integration not implemented yet. "
            "X11: XQueryPointer / XTestFakeMotionEvent. "
            "Wayland: portal / ydotool (no universal warp API)."
        )

    def set_position(self, x: int, y: int) -> None:
        raise NotImplementedError(
            "Linux cursor integration not implemented yet. "
            "X11: XTestFakeMotionEvent. Wayland: ydotool or compositor-specific APIs."
        )
