"""Landmark extraction interfaces and MediaPipe/mock implementations."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Protocol

from .data import LANDMARKS_VERSION, LandmarkFrame, LandmarkPoint, LandmarkSequence
from .vocabulary import Vocabulary, load_housing_repair_vocabulary


class MissingVisionDependency(RuntimeError):
    """Raised when an optional camera/landmark dependency is not installed."""


class LandmarkExtractor(Protocol):
    """Extract a landmark sequence for one local sign clip."""

    def extract_clip(
        self,
        clip_path: Path,
        *,
        clip_id: str,
        phrase_id: str,
        signer_id: str,
        take_id: str,
        tokens: tuple[str, ...],
    ) -> LandmarkSequence:
        """Return landmarks for one local clip path."""


class MediaPipeHolisticExtractor:
    """MediaPipe Holistic extractor scaffold.

    Importing this class does not require MediaPipe or OpenCV. The dependencies
    are imported only when extraction starts so offline mock paths still work.
    """

    landmarks_version = LANDMARKS_VERSION

    def __init__(
        self,
        *,
        include_face: bool = False,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self.include_face = include_face
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

    def extract_clip(
        self,
        clip_path: Path,
        *,
        clip_id: str,
        phrase_id: str,
        signer_id: str,
        take_id: str,
        tokens: tuple[str, ...],
    ) -> LandmarkSequence:
        cv2, mp = self._load_dependencies()
        capture = cv2.VideoCapture(str(clip_path))
        if not capture.isOpened():
            raise FileNotFoundError(f"Could not open sign clip: {clip_path}")

        fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
        frames: list[LandmarkFrame] = []

        with mp.solutions.holistic.Holistic(
            static_image_mode=False,
            model_complexity=self.model_complexity,
            smooth_landmarks=True,
            enable_segmentation=False,
            refine_face_landmarks=False,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        ) as holistic:
            frame_index = 0
            while True:
                ok, image_bgr = capture.read()
                if not ok:
                    break

                image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                result = holistic.process(image_rgb)
                t_ms = int(capture.get(cv2.CAP_PROP_POS_MSEC) or (frame_index * 1000 / fps))
                points = self._result_points(result)
                if points:
                    frames.append(LandmarkFrame(t_ms=t_ms, frame_index=frame_index, points=tuple(points)))
                frame_index += 1

        capture.release()
        if not frames:
            raise ValueError(f"No landmarks extracted from {clip_path}")

        return LandmarkSequence(
            clip_id=clip_id,
            phrase_id=phrase_id,
            signer_id=signer_id,
            take_id=take_id,
            tokens=tokens,
            frames=tuple(frames),
            source_clip_path=str(clip_path),
            metadata={"extractor": "mediapipe_holistic", "include_face": self.include_face},
        )

    def _load_dependencies(self):
        try:
            import cv2  # type: ignore[import-not-found]
            import mediapipe as mp  # type: ignore[import-not-found]
        except ImportError as exc:
            raise MissingVisionDependency(
                "MediaPipe extraction requires optional dependencies: mediapipe and opencv-python. "
                "Use MockLandmarkExtractor for offline tests or install the camera stack before extraction."
            ) from exc
        return cv2, mp

    def _result_points(self, result) -> list[LandmarkPoint]:
        points: list[LandmarkPoint] = []
        points.extend(_landmark_list_points("pose", result.pose_landmarks))
        points.extend(_landmark_list_points("left_hand", result.left_hand_landmarks))
        points.extend(_landmark_list_points("right_hand", result.right_hand_landmarks))
        if self.include_face:
            points.extend(_landmark_list_points("face", result.face_landmarks))
        return points


def _landmark_list_points(landmark_set: str, landmark_list) -> list[LandmarkPoint]:
    if landmark_list is None:
        return []
    points: list[LandmarkPoint] = []
    for index, landmark in enumerate(landmark_list.landmark):
        points.append(
            LandmarkPoint(
                landmark_set=landmark_set,
                index=index,
                x=float(landmark.x),
                y=float(landmark.y),
                z=float(getattr(landmark, "z", 0.0)),
                visibility=(
                    float(landmark.visibility)
                    if hasattr(landmark, "visibility")
                    else None
                ),
                presence=(
                    float(landmark.presence)
                    if hasattr(landmark, "presence")
                    else None
                ),
            )
        )
    return points


class MockLandmarkExtractor:
    """Deterministic landmark generator for tests and provider-unavailable demos."""

    def __init__(self, *, vocabulary: Vocabulary | None = None, frames: int = 18, noise: float = 0.0) -> None:
        self.vocabulary = vocabulary or load_housing_repair_vocabulary()
        self.frames = frames
        self.noise = noise

    def extract_clip(
        self,
        clip_path: Path,
        *,
        clip_id: str,
        phrase_id: str,
        signer_id: str,
        take_id: str,
        tokens: tuple[str, ...],
    ) -> LandmarkSequence:
        return self.make_sequence(
            phrase_id=phrase_id,
            signer_id=signer_id,
            take_id=take_id,
            clip_id=clip_id,
            tokens=tokens,
            source_clip_path=str(clip_path),
        )

    def make_sequence(
        self,
        *,
        phrase_id: str,
        signer_id: str = "mock-signer",
        take_id: str = "take-001",
        clip_id: str | None = None,
        tokens: tuple[str, ...] | None = None,
        source_clip_path: str | None = None,
    ) -> LandmarkSequence:
        entry = self.vocabulary.get(phrase_id)
        tokens = tokens or entry.tokens
        clip_id = clip_id or f"{phrase_id}-{signer_id}-{take_id}"
        seed = int(hashlib.sha256(f"{phrase_id}:{signer_id}:{take_id}".encode("utf-8")).hexdigest()[:8], 16)
        phrase_seed = int(hashlib.sha256(phrase_id.encode("utf-8")).hexdigest()[:8], 16)
        phase = (phrase_seed % 360) * math.pi / 180.0
        amplitude = 0.08 + (phrase_seed % 7) * 0.012
        hand_bias = ((phrase_seed // 7) % 9 - 4) * 0.012
        frames: list[LandmarkFrame] = []

        for frame_index in range(self.frames):
            progress = frame_index / max(self.frames - 1, 1)
            jitter = self._jitter(seed, frame_index)
            wave = math.sin(progress * math.pi * 2.0 + phase)
            sweep = math.cos(progress * math.pi + phase / 2.0)
            left_x = 0.38 + hand_bias + amplitude * wave + jitter
            right_x = 0.62 - hand_bias - amplitude * wave - jitter
            left_y = 0.58 - amplitude * 0.75 * sweep
            right_y = 0.58 + amplitude * 0.5 * sweep
            points = (
                LandmarkPoint("pose", 11, 0.42, 0.42, 0.0, 0.99),
                LandmarkPoint("pose", 12, 0.58, 0.42, 0.0, 0.99),
                LandmarkPoint("pose", 15, left_x, left_y, 0.01 * wave, 0.98),
                LandmarkPoint("pose", 16, right_x, right_y, -0.01 * wave, 0.98),
                LandmarkPoint("left_hand", 0, left_x, left_y, 0.0, 0.98),
                LandmarkPoint("left_hand", 8, left_x - 0.035, left_y - 0.08, 0.0, 0.98),
                LandmarkPoint("right_hand", 0, right_x, right_y, 0.0, 0.98),
                LandmarkPoint("right_hand", 8, right_x + 0.035, right_y - 0.08, 0.0, 0.98),
            )
            frames.append(LandmarkFrame(t_ms=frame_index * 33, frame_index=frame_index, points=points))

        return LandmarkSequence(
            clip_id=clip_id,
            phrase_id=phrase_id,
            signer_id=signer_id,
            take_id=take_id,
            tokens=tokens,
            frames=tuple(frames),
            source_clip_path=source_clip_path,
            metadata={"extractor": "mock", "synthetic": True, "limitation": "not real signing data"},
        )

    def make_dataset(self, *, takes_per_phrase: int = 3, signer_id: str = "mock-signer") -> list[LandmarkSequence]:
        sequences: list[LandmarkSequence] = []
        for entry in self.vocabulary.entries:
            for take_number in range(1, takes_per_phrase + 1):
                sequences.append(
                    self.make_sequence(
                        phrase_id=entry.phrase_id,
                        signer_id=signer_id,
                        take_id=f"take-{take_number:03d}",
                    )
                )
        return sequences

    def _jitter(self, seed: int, frame_index: int) -> float:
        if self.noise <= 0:
            return 0.0
        value = math.sin(seed * 0.001 + frame_index * 12.9898) * 43758.5453
        fractional = value - math.floor(value)
        return (fractional - 0.5) * self.noise

