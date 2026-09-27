"""Magnetic snap math — pure functions, no OS calls."""

from __future__ import annotations

import math
from dataclasses import dataclass

from kill_mouse.config import Config, DEFAULT
from kill_mouse.inference import Detection


@dataclass(frozen=True)
class SnapResult:
    x: float
    y: float
    snapped: bool
    target: Detection | None
    distance: float


def _distance_point_to_bbox(px: float, py: float, bbox: tuple[float, float, float, float]) -> float:
    x1, y1, x2, y2 = bbox
    cx = min(max(px, x1), x2)
    cy = min(max(py, y1), y2)
    return math.hypot(px - cx, py - cy)


def _velocity(prev: tuple[float, float] | None, curr: tuple[float, float]) -> tuple[float, float]:
    if prev is None:
        return (0.0, 0.0)
    return (curr[0] - prev[0], curr[1] - prev[1])


def compute_snap(
    raw_x: float,
    raw_y: float,
    detections: list[Detection],
    prev_pos: tuple[float, float] | None = None,
    config: Config = DEFAULT,
) -> SnapResult:
    """
    If the cursor is within activation_radius of a detection, pull toward its
    center. Prefer the candidate closest to the current trajectory when several
    are in range.
    """
    if not detections:
        return SnapResult(raw_x, raw_y, False, None, math.inf)

    vx, vy = _velocity(prev_pos, (raw_x, raw_y))
    speed = math.hypot(vx, vy)

    candidates: list[tuple[float, float, Detection]] = []
    for det in detections:
        dist = _distance_point_to_bbox(raw_x, raw_y, det.bbox)
        if dist > config.activation_radius_px:
            continue

        # Trajectory score: prefer boxes ahead of motion.
        dx = det.center[0] - raw_x
        dy = det.center[1] - raw_y
        if speed > 0.5:
            # Higher (less negative / more positive) alignment is better.
            alignment = (vx * dx + vy * dy) / (speed * (math.hypot(dx, dy) + 1e-6))
        else:
            alignment = 0.0

        # Rank by distance primarily; break ties with alignment.
        rank = dist - 0.5 * alignment
        candidates.append((rank, dist, det))

    if not candidates:
        return SnapResult(raw_x, raw_y, False, None, math.inf)

    candidates.sort(key=lambda t: t[0])
    _, dist, target = candidates[0]

    cx, cy = target.center
    to_center_x = cx - raw_x
    to_center_y = cy - raw_y
    to_center_len = math.hypot(to_center_x, to_center_y) + 1e-6

    x1, y1, x2, y2 = target.bbox
    inside = x1 <= raw_x <= x2 and y1 <= raw_y <= y2
    strength = config.inside_strength if inside else config.snap_strength

    # Release when not clearly moving toward the target center.
    if speed > 0.5:
        toward_dot = (vx * to_center_x + vy * to_center_y) / (speed * to_center_len)
        if toward_dot < config.escape_dot_threshold:
            # Blend from full strength → escape_strength as motion aims away.
            t = (config.escape_dot_threshold - toward_dot) / (
                config.escape_dot_threshold - (-1.0) + 1e-6
            )
            t = max(0.0, min(1.0, t))
            strength = strength * (1.0 - t) + config.escape_strength * t

    final_x = raw_x + (cx - raw_x) * strength
    final_y = raw_y + (cy - raw_y) * strength
    return SnapResult(final_x, final_y, True, target, dist)
