"""On-screen debug overlay — platform factory."""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod

from mouse_aimbot.inference import Detection


class DebugOverlay(ABC):
    @abstractmethod
    def update(
        self,
        detections: list[Detection],
        snapped: Detection | None,
        monitor: dict[str, int],
    ) -> None:
        ...

    @abstractmethod
    def pump(self) -> None:
        """Process UI events; call from the main thread periodically."""

    @abstractmethod
    def close(self) -> None:
        ...


def get_debug_overlay() -> DebugOverlay:
    if sys.platform == "win32":
        from mouse_aimbot.platform.windows.overlay import WindowsDebugOverlay

        return WindowsDebugOverlay()
    raise NotImplementedError(
        f"Debug overlay not implemented for {sys.platform} yet. "
        "Windows overlay is the MVP path."
    )
