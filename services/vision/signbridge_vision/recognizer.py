"""Baseline constrained recognizers for landmark sequences."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Literal

from .data import LandmarkSequence
from .normalization import (
    Layout,
    infer_landmark_layout,
    resample_vectors,
    sequence_to_vectors,
    vector_distance,
)
from .vocabulary import Vocabulary, VocabularyEntry


RecognitionMethod = Literal["dtw", "centroid"]


@dataclass(frozen=True)
class RecognizerConfig:
    """Tunable confidence and matching settings."""

    method: RecognitionMethod = "dtw"
    top_k: int = 3
    partial_threshold: float = 0.55
    final_threshold: float = 0.72
    confidence_distance_scale: float = 2.4
    centroid_frames: int = 24


@dataclass(frozen=True)
class RecognitionCandidate:
    phrase_id: str
    tokens: tuple[str, ...]
    label: str
    distance: float
    confidence: float
    rank: int


@dataclass(frozen=True)
class _Template:
    phrase_id: str
    tokens: tuple[str, ...]
    label: str
    vectors: list[list[float]]
    clip_id: str
    signer_id: str
    take_id: str


class TemplateDTWRecognizer:
    """Template matcher with DTW and a nearest-centroid option.

    This is deliberately simple and auditable. It is intended for the constrained
    housing repair demo vocabulary, not general BSL translation.
    """

    def __init__(
        self,
        templates: Iterable[LandmarkSequence],
        *,
        vocabulary: Vocabulary,
        config: RecognizerConfig | None = None,
        layout: Layout | None = None,
    ) -> None:
        self.vocabulary = vocabulary
        self.config = config or RecognizerConfig()
        template_sequences = tuple(templates)
        if not template_sequences:
            raise ValueError("Recognizer requires at least one template sequence")

        self.layout = layout or infer_landmark_layout(template_sequences)
        self.templates = tuple(self._make_template(sequence) for sequence in template_sequences)
        self._centroids = self._build_centroids()

    def _entry_for(self, sequence: LandmarkSequence) -> VocabularyEntry:
        try:
            return self.vocabulary.get(sequence.phrase_id)
        except KeyError:
            return VocabularyEntry(
                phrase_id=sequence.phrase_id,
                display=sequence.phrase_id.replace("_", " ").title(),
                tokens=sequence.tokens,
                english_hint="Unknown phrase from landmark data.",
            )

    def _make_template(self, sequence: LandmarkSequence) -> _Template:
        entry = self._entry_for(sequence)
        return _Template(
            phrase_id=sequence.phrase_id,
            tokens=entry.tokens,
            label=entry.display,
            vectors=sequence_to_vectors(sequence, self.layout),
            clip_id=sequence.clip_id,
            signer_id=sequence.signer_id,
            take_id=sequence.take_id,
        )

    def recognize(self, sequence: LandmarkSequence) -> list[RecognitionCandidate]:
        sample_vectors = sequence_to_vectors(sequence, self.layout)
        if self.config.method == "centroid":
            scored = self._score_centroids(sample_vectors)
        else:
            scored = self._score_templates(sample_vectors)

        scored.sort(key=lambda item: item[1])
        top = scored[: max(self.config.top_k, 1)]
        second_distance = scored[1][1] if len(scored) > 1 else top[0][1] * 1.5 + 1e-6

        candidates = [
            RecognitionCandidate(
                phrase_id=phrase_id,
                tokens=self.vocabulary.get(phrase_id).tokens,
                label=self.vocabulary.get(phrase_id).display,
                distance=distance,
                confidence=self._confidence(distance, second_distance),
                rank=rank,
            )
            for rank, (phrase_id, distance) in enumerate(top, start=1)
        ]
        return candidates

    def _score_templates(self, sample_vectors: list[list[float]]) -> list[tuple[str, float]]:
        nearest_by_phrase: dict[str, float] = {}
        for template in self.templates:
            distance = dtw_distance(sample_vectors, template.vectors)
            current = nearest_by_phrase.get(template.phrase_id)
            if current is None or distance < current:
                nearest_by_phrase[template.phrase_id] = distance
        return list(nearest_by_phrase.items())

    def _build_centroids(self) -> dict[str, list[list[float]]]:
        grouped: dict[str, list[list[list[float]]]] = defaultdict(list)
        for template in self.templates:
            grouped[template.phrase_id].append(
                resample_vectors(template.vectors, self.config.centroid_frames)
            )

        centroids: dict[str, list[list[float]]] = {}
        for phrase_id, sequences in grouped.items():
            frame_count = len(sequences[0])
            dimensions = len(sequences[0][0]) if sequences[0] else 0
            centroid: list[list[float]] = []
            for frame_index in range(frame_count):
                centroid.append([
                    sum(sequence[frame_index][dim] for sequence in sequences) / len(sequences)
                    for dim in range(dimensions)
                ])
            centroids[phrase_id] = centroid
        return centroids

    def _score_centroids(self, sample_vectors: list[list[float]]) -> list[tuple[str, float]]:
        sample = resample_vectors(sample_vectors, self.config.centroid_frames)
        scored: list[tuple[str, float]] = []
        for phrase_id, centroid in self._centroids.items():
            frame_distances = [
                vector_distance(sample_frame, centroid_frame)
                for sample_frame, centroid_frame in zip(sample, centroid)
            ]
            scored.append((phrase_id, sum(frame_distances) / len(frame_distances)))
        return scored

    def _confidence(self, best_distance: float, second_distance: float) -> float:
        distance_score = 1.0 / (1.0 + best_distance * self.config.confidence_distance_scale)
        margin = max(second_distance - best_distance, 0.0) / max(second_distance, 1e-6)
        confidence = distance_score * 0.88 + min(margin, 1.0) * 0.12
        return max(0.0, min(1.0, confidence))


def dtw_distance(left: list[list[float]], right: list[list[float]]) -> float:
    """Dynamic time warping distance normalized by path length."""

    if not left or not right:
        return math.inf

    rows = len(left) + 1
    cols = len(right) + 1
    costs = [[math.inf] * cols for _ in range(rows)]
    steps = [[0] * cols for _ in range(rows)]
    costs[0][0] = 0.0

    for row in range(1, rows):
        for col in range(1, cols):
            choices = (
                (costs[row - 1][col], steps[row - 1][col]),
                (costs[row][col - 1], steps[row][col - 1]),
                (costs[row - 1][col - 1], steps[row - 1][col - 1]),
            )
            previous_cost, previous_steps = min(choices, key=lambda item: item[0])
            costs[row][col] = previous_cost + vector_distance(left[row - 1], right[col - 1])
            steps[row][col] = previous_steps + 1

    return costs[-1][-1] / max(steps[-1][-1], 1)

