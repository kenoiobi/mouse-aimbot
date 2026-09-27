"""Runtime defaults for the MVP."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # TargetFinder (UI-trained YOLO26) — see NOTICE for upstream credit.
    model_name: str = "yolo26n-640"
    change_thresh: int = 100
    # Poll / re-infer cadence. Lower = hotter CPU; 30 FPS is overkill for UI.
    capture_interval_s: float = 0.35
    conf_threshold: float = 0.4
    iou_threshold: float = 0.3

    # Magnetic snap — kept intentionally soft so handoff between targets is easy.
    activation_radius_px: float = 36.0
    snap_strength: float = 0.22
    # Any motion not clearly toward center starts releasing (was -0.2 = only hard push-away).
    escape_dot_threshold: float = 0.15
    # Once inside the box, barely hold — lets you walk out without fighting.
    inside_strength: float = 0.04
    escape_strength: float = 0.0

    # Cursor poll / overlay refresh (ms)
    overlay_tick_ms: int = 8

    # Overlay (debug)
    overlay_enabled: bool = True
    overlay_candidate_rgb: tuple[int, int, int] = (0, 200, 255)
    overlay_snapped_rgb: tuple[int, int, int] = (0, 255, 100)
    overlay_line_width: int = 2
    overlay_snapped_line_width: int = 3

    # Safety
    quit_hotkey: str = "<ctrl>+<alt>+q"

    # Display
    # TODO(multi-monitor): TargetFinder already paints per-screen; snap still
    # assumes one logical desktop. Re-test multi-monitor later.
    primary_monitor_only: bool = True


DEFAULT = Config()
