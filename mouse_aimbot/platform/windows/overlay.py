"""
Click-through, topmost debug overlay for Windows.

Uses a layered transparent Tk window with a chroma-key color so only the
drawn outlines are visible. WS_EX_TRANSPARENT / WS_EX_LAYERED / WS_EX_TOPMOST
keep it from stealing mouse input.
"""

from __future__ import annotations

import tkinter as tk

from mouse_aimbot.config import DEFAULT
from mouse_aimbot.inference import Detection
from mouse_aimbot.overlay import DebugOverlay

# Pure magenta chroma key — must not appear in outline colors.
_TRANSPARENT = "#ff00ff"


class WindowsDebugOverlay(DebugOverlay):
    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.title("mouse-aimbot debug")
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        try:
            self._root.attributes("-transparentcolor", _TRANSPARENT)
        except tk.TclError:
            self._root.attributes("-alpha", 0.35)

        self._canvas = tk.Canvas(self._root, highlightthickness=0, bg=_TRANSPARENT)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._monitor: dict[str, int] | None = None
        self._hwnd_styled = False
        self._closed = False

        self._root.geometry("1x1+0+0")
        self._root.update_idletasks()
        self._apply_clickthrough()

    def _apply_clickthrough(self) -> None:
        try:
            import win32con
            import win32gui

            handles = {int(self._root.winfo_id()), int(self._canvas.winfo_id())}
            for handle in handles:
                style = win32gui.GetWindowLong(handle, win32con.GWL_EXSTYLE)
                style |= (
                    win32con.WS_EX_LAYERED
                    | win32con.WS_EX_TRANSPARENT
                    | win32con.WS_EX_TOOLWINDOW
                    | win32con.WS_EX_NOACTIVATE
                )
                win32gui.SetWindowLong(handle, win32con.GWL_EXSTYLE, style)
            self._hwnd_styled = True
        except Exception:
            self._hwnd_styled = True

    def _ensure_geometry(self, monitor: dict[str, int]) -> None:
        if self._monitor == monitor:
            return
        self._monitor = dict(monitor)
        left = monitor["left"]
        top = monitor["top"]
        width = monitor["width"]
        height = monitor["height"]
        self._root.geometry(f"{width}x{height}+{left}+{top}")
        self._canvas.config(width=width, height=height)
        self._root.update_idletasks()
        self._apply_clickthrough()

    def update(
        self,
        detections: list[Detection],
        snapped: Detection | None,
        monitor: dict[str, int],
    ) -> None:
        if self._closed:
            return
        self._ensure_geometry(monitor)
        left = monitor["left"]
        top = monitor["top"]

        self._canvas.delete("all")
        candidate = "#%02x%02x%02x" % DEFAULT.overlay_candidate_color
        snapped_color = "#%02x%02x%02x" % DEFAULT.overlay_snapped_color

        for det in detections:
            x1, y1, x2, y2 = det.bbox
            lx1, ly1 = x1 - left, y1 - top
            lx2, ly2 = x2 - left, y2 - top
            is_snapped = snapped is not None and (
                det is snapped
                or (
                    abs(det.center[0] - snapped.center[0]) < 0.5
                    and abs(det.center[1] - snapped.center[1]) < 0.5
                )
            )
            color = snapped_color if is_snapped else candidate
            width = (
                DEFAULT.overlay_snapped_line_width if is_snapped else DEFAULT.overlay_line_width
            )
            self._canvas.create_rectangle(
                lx1, ly1, lx2, ly2, outline=color, width=width, fill=""
            )
            self._canvas.create_text(
                lx1 + 4,
                ly1 + 4,
                text=f"{det.class_name} {det.confidence:.2f}",
                anchor="nw",
                fill=color,
                font=("Segoe UI", 9),
            )

    def pump(self) -> None:
        if self._closed:
            return
        try:
            self._root.update_idletasks()
            self._root.update()
        except tk.TclError:
            self._closed = True

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._root.destroy()
        except tk.TclError:
            pass
