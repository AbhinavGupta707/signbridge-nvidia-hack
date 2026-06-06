"""High-level constrained recognition pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from .data import LandmarkSequence
from .events import RecognitionEmission, RecognitionEventEmitter
from .extractors import MockLandmarkExtractor
from .recognizer import RecognizerConfig, TemplateDTWRecognizer
from .vocabulary import Vocabulary, load_housing_repair_vocabulary


@dataclass
class VisionRecognitionPipeline:
    """Recognize one completed landmark sequence and emit shared events."""

    recognizer: TemplateDTWRecognizer
    emitter: RecognitionEventEmitter

    def recognize_sequence(
        self,
        sequence: LandmarkSequence,
        *,
        session_id: str,
        utterance_id: str | None = None,
        t_ms: int | None = None,
    ) -> RecognitionEmission:
        candidates = self.recognizer.recognize(sequence)
        return self.emitter.emit(candidates, session_id=session_id, utterance_id=utterance_id, t_ms=t_ms)


def build_mock_pipeline(
    *,
    vocabulary: Vocabulary | None = None,
    takes_per_phrase: int = 3,
    config: RecognizerConfig | None = None,
) -> VisionRecognitionPipeline:
    """Build a deterministic mock pipeline for local smoke tests."""

    vocabulary = vocabulary or load_housing_repair_vocabulary()
    config = config or RecognizerConfig()
    extractor = MockLandmarkExtractor(vocabulary=vocabulary, noise=0.002)
    templates = extractor.make_dataset(takes_per_phrase=takes_per_phrase)
    recognizer = TemplateDTWRecognizer(templates, vocabulary=vocabulary, config=config)
    emitter = RecognitionEventEmitter(config=config)
    return VisionRecognitionPipeline(recognizer=recognizer, emitter=emitter)

