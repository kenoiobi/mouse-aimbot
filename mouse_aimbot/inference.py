"""Detection types + conversion from TargetFinder outputs."""

from __future__ import annotations

from dataclasses import dataclass

from target_finder_toolkit.targetfinder import CLASS_NAMES


@dataclass(frozen=True)
class Detection:
    class_name: str
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2 (logical screen)
    center: tuple[float, float]
    confidence: float

    def as_dict(self) -> dict:
        return {
            "class": self.class_name,
            "bbox": list(self.bbox),
            "center": list(self.center),
            "confidence": self.confidence,
        }


def from_targetfinder_tuple(det: tuple) -> Detection:
    """Convert TargetFinder ``(x, y, w, h, score, class_id)`` → Detection."""
    x, y, w, h, score, cls_id = det
    x1, y1 = float(x), float(y)
    x2, y2 = x1 + float(w), y1 + float(h)
    return Detection(
        class_name=CLASS_NAMES.get(int(cls_id), str(int(cls_id))),
        bbox=(x1, y1, x2, y2),
        center=((x1 + x2) / 2.0, (y1 + y2) / 2.0),
        confidence=float(score),
    )


def detections_from_targetfinder(raw: list[tuple]) -> list[Detection]:
    return [from_targetfinder_tuple(t) for t in raw]
