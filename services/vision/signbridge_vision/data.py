"""Local landmark sequence data structures and JSONL I/O."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


LANDMARKS_VERSION = "mediapipe_holistic_v1"


@dataclass(frozen=True)
class LandmarkPoint:
    """A single normalized MediaPipe-style landmark point."""

    landmark_set: str
    index: int
    x: float
    y: float
    z: float = 0.0
    visibility: float | None = None
    presence: float | None = None

    @property
    def key(self) -> str:
        return f"{self.landmark_set}:{self.index}"

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LandmarkPoint":
        return cls(
            landmark_set=str(payload["landmark_set"]),
            index=int(payload["index"]),
            x=float(payload["x"]),
            y=float(payload["y"]),
            z=float(payload.get("z", 0.0)),
            visibility=(
                float(payload["visibility"])
                if payload.get("visibility") is not None
                else None
            ),
            presence=(
                float(payload["presence"])
                if payload.get("presence") is not None
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "landmark_set": self.landmark_set,
            "index": self.index,
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }
        if self.visibility is not None:
            payload["visibility"] = self.visibility
        if self.presence is not None:
            payload["presence"] = self.presence
        return payload


@dataclass(frozen=True)
class LandmarkFrame:
    """All selected landmarks for one video frame."""

    t_ms: int
    points: tuple[LandmarkPoint, ...]
    frame_index: int | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LandmarkFrame":
        points = payload.get("points")
        if not isinstance(points, list):
            raise ValueError("LandmarkFrame requires points array")

        return cls(
            t_ms=int(payload["t_ms"]),
            points=tuple(LandmarkPoint.from_dict(point) for point in points),
            frame_index=(
                int(payload["frame_index"])
                if payload.get("frame_index") is not None
                else None
            ),
        )

    def point_map(self) -> dict[str, LandmarkPoint]:
        return {point.key: point for point in self.points}

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "t_ms": self.t_ms,
            "points": [point.to_dict() for point in self.points],
        }
        if self.frame_index is not None:
            payload["frame_index"] = self.frame_index
        return payload


@dataclass(frozen=True)
class LandmarkSequence:
    """One signed phrase clip after landmark extraction."""

    clip_id: str
    phrase_id: str
    signer_id: str
    take_id: str
    tokens: tuple[str, ...]
    frames: tuple[LandmarkFrame, ...]
    scenario: str = "housing_repair"
    landmarks_version: str = LANDMARKS_VERSION
    source_clip_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> int:
        if not self.frames:
            return 0
        return max(frame.t_ms for frame in self.frames) - min(frame.t_ms for frame in self.frames)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LandmarkSequence":
        frames = payload.get("frames")
        if not isinstance(frames, list) or not frames:
            raise ValueError(f"Landmark sequence {payload.get('clip_id')} requires non-empty frames")

        tokens = payload.get("tokens")
        if not isinstance(tokens, list) or not tokens:
            raise ValueError(f"Landmark sequence {payload.get('clip_id')} requires non-empty tokens")

        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object when present")

        return cls(
            clip_id=str(payload["clip_id"]),
            phrase_id=str(payload["phrase_id"]),
            signer_id=str(payload["signer_id"]),
            take_id=str(payload["take_id"]),
            tokens=tuple(str(token) for token in tokens),
            frames=tuple(LandmarkFrame.from_dict(frame) for frame in frames),
            scenario=str(payload.get("scenario", "housing_repair")),
            landmarks_version=str(payload.get("landmarks_version", LANDMARKS_VERSION)),
            source_clip_path=(
                str(payload["source_clip_path"])
                if payload.get("source_clip_path") is not None
                else None
            ),
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "clip_id": self.clip_id,
            "phrase_id": self.phrase_id,
            "signer_id": self.signer_id,
            "take_id": self.take_id,
            "scenario": self.scenario,
            "tokens": list(self.tokens),
            "landmarks_version": self.landmarks_version,
            "frames": [frame.to_dict() for frame in self.frames],
            "metadata": self.metadata,
        }
        if self.source_clip_path is not None:
            payload["source_clip_path"] = self.source_clip_path
        return payload


def load_landmark_jsonl(path: Path) -> list[LandmarkSequence]:
    """Load one landmark sequence per line from the local JSONL format."""

    sequences: list[LandmarkSequence] = []
    with path.open("r", encoding="utf-8") as landmarks_file:
        for line_number, line in enumerate(landmarks_file, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                sequences.append(LandmarkSequence.from_dict(json.loads(stripped)))
            except Exception as exc:  # noqa: BLE001 - include line context for data triage.
                raise ValueError(f"{path}:{line_number}: invalid landmark sequence: {exc}") from exc

    return sequences


def write_landmark_jsonl(path: Path, sequences: Iterable[LandmarkSequence]) -> None:
    """Write landmark sequences in the local JSONL format."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as landmarks_file:
        for sequence in sequences:
            landmarks_file.write(json.dumps(sequence.to_dict(), separators=(",", ":")) + "\n")

