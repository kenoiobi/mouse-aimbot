"""Screen capture — primary monitor only for MVP."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# TODO(multi-monitor): iterate mss monitors[1:], map global virtual-desktop
# coordinates, and place one overlay per display (or one spanning the virtual
# screen). Primary-only is intentional for the MVP.


@dataclass(frozen=True)
class Frame:
    """BGR image plus the monitor origin in virtual-desktop coordinates."""

    image_bgr: np.ndarray
    left: int
    top: int
    width: int
    height: int


class ScreenCapture:
    def __init__(self) -> None:
        import mss

        self._mss = mss.mss()
        # mss: monitors[0] = virtual desktop, monitors[1] = primary
        self._monitor = self._mss.monitors[1]

    def grab(self) -> Frame:
        shot = self._mss.grab(self._monitor)
        # mss returns BGRA
        bgra = np.asarray(shot, dtype=np.uint8)
        bgr = bgra[:, :, :3].copy()
        return Frame(
            image_bgr=bgr,
            left=int(self._monitor["left"]),
            top=int(self._monitor["top"]),
            width=int(self._monitor["width"]),
            height=int(self._monitor["height"]),
        )

    def close(self) -> None:
        self._mss.close()
