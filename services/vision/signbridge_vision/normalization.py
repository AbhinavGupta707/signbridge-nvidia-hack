"""Feature normalization for landmark-sequence matching."""

from __future__ import annotations

import math
from collections import Counter
from typing import Iterable

from .data import LandmarkFrame, LandmarkPoint, LandmarkSequence


Layout = tuple[str, ...]

LANDMARK_SET_ORDER = {
    "pose": 0,
    "left_hand": 1,
    "right_hand": 2,
    "face": 3,
}


def landmark_sort_key(key: str) -> tuple[int, int, str]:
    landmark_set, _, raw_index = key.partition(":")
    try:
        index = int(raw_index)
    except ValueError:
        index = 9999
    return (LANDMARK_SET_ORDER.get(landmark_set, 99), index, key)


def infer_landmark_layout(
    sequences: Iterable[LandmarkSequence],
    *,
    min_frame_coverage: float = 0.1,
) -> Layout:
    """Infer a stable vector layout from observed landmark keys."""

    counts: Counter[str] = Counter()
    frame_count = 0
    for sequence in sequences:
        for frame in sequence.frames:
            frame_count += 1
            counts.update(point.key for point in frame.points)

    if frame_count == 0:
        raise ValueError("Cannot infer landmark layout from empty sequences")

    keys = [
        key
        for key, count in counts.items()
        if count / frame_count >= min_frame_coverage
    ]
    if not keys:
        raise ValueError("Cannot infer landmark layout: no landmarks meet coverage threshold")

    return tuple(sorted(keys, key=landmark_sort_key))


def _point_xy(point: LandmarkPoint | None) -> tuple[float, float] | None:
    if point is None:
        return None
    if point.visibility is not None and point.visibility < 0.2:
        return None
    return (point.x, point.y)


def _center_and_scale(point_map: dict[str, LandmarkPoint]) -> tuple[float, float, float]:
    left_shoulder = _point_xy(point_map.get("pose:11"))
    right_shoulder = _point_xy(point_map.get("pose:12"))
    if left_shoulder and right_shoulder:
        cx = (left_shoulder[0] + right_shoulder[0]) / 2.0
        cy = (left_shoulder[1] + right_shoulder[1]) / 2.0
        scale = math.dist(left_shoulder, right_shoulder)
        return cx, cy, max(scale, 1e-6)

    visible = [
        (point.x, point.y)
        for point in point_map.values()
        if point.visibility is None or point.visibility >= 0.2
    ]
    if not visible:
        return 0.0, 0.0, 1.0

    cx = sum(x for x, _ in visible) / len(visible)
    cy = sum(y for _, y in visible) / len(visible)
    min_x = min(x for x, _ in visible)
    max_x = max(x for x, _ in visible)
    min_y = min(y for _, y in visible)
    max_y = max(y for _, y in visible)
    scale = math.dist((min_x, min_y), (max_x, max_y))
    return cx, cy, max(scale, 1e-6)


def frame_to_vector(frame: LandmarkFrame, layout: Layout) -> list[float]:
    """Convert a frame into a centered, scale-normalized feature vector."""

    point_map = frame.point_map()
    cx, cy, scale = _center_and_scale(point_map)
    vector: list[float] = []
    for key in layout:
        point = point_map.get(key)
        if point is None or (point.visibility is not None and point.visibility < 0.2):
            vector.extend((0.0, 0.0, 0.0))
            continue
        vector.extend(((point.x - cx) / scale, (point.y - cy) / scale, point.z / scale))
    return vector


def sequence_to_vectors(sequence: LandmarkSequence, layout: Layout) -> list[list[float]]:
    return [frame_to_vector(frame, layout) for frame in sequence.frames]


def vector_distance(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Feature vectors must have the same length")
    if not left:
        return 0.0
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)) / len(left))


def resample_vectors(vectors: list[list[float]], target_frames: int) -> list[list[float]]:
    """Linearly resample a sequence for centroid baselines."""

    if target_frames <= 0:
        raise ValueError("target_frames must be positive")
    if not vectors:
        return []
    if len(vectors) == 1:
        return [list(vectors[0]) for _ in range(target_frames)]
    if len(vectors) == target_frames:
        return [list(vector) for vector in vectors]

    result: list[list[float]] = []
    last_index = len(vectors) - 1
    for output_index in range(target_frames):
        position = output_index * last_index / max(target_frames - 1, 1)
        lower = int(math.floor(position))
        upper = min(lower + 1, last_index)
        weight = position - lower
        result.append([
            vectors[lower][dim] * (1.0 - weight) + vectors[upper][dim] * weight
            for dim in range(len(vectors[0]))
        ])
    return result

