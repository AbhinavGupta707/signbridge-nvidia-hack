from __future__ import annotations

import unittest

from services.vision.signbridge_vision.events import RecognitionEventEmitter
from services.vision.signbridge_vision.extractors import MockLandmarkExtractor
from services.vision.signbridge_vision.recognizer import RecognitionCandidate, RecognizerConfig, TemplateDTWRecognizer
from services.vision.signbridge_vision.vocabulary import load_housing_repair_vocabulary


class VisionRecognizerTests(unittest.TestCase):
    def test_vocabulary_is_constrained(self) -> None:
        vocabulary = load_housing_repair_vocabulary()
        self.assertGreaterEqual(len(vocabulary.entries), 20)
        self.assertLessEqual(len(vocabulary.entries), 35)
        self.assertIn("DAMP_IN_HOME", vocabulary.phrase_ids())

    def test_mock_sequence_matches_nearest_template(self) -> None:
        vocabulary = load_housing_repair_vocabulary()
        extractor = MockLandmarkExtractor(vocabulary=vocabulary, noise=0.001)
        templates = extractor.make_dataset(takes_per_phrase=3)
        recognizer = TemplateDTWRecognizer(templates, vocabulary=vocabulary)

        sample = extractor.make_sequence(
            phrase_id="DAMP_IN_HOME",
            signer_id="held-out",
            take_id="take-001",
        )
        candidates = recognizer.recognize(sample)

        self.assertEqual(candidates[0].phrase_id, "DAMP_IN_HOME")
        self.assertGreaterEqual(candidates[0].confidence, 0.72)

    def test_event_emitter_returns_contract_compatible_partial_and_final(self) -> None:
        vocabulary = load_housing_repair_vocabulary()
        extractor = MockLandmarkExtractor(vocabulary=vocabulary, noise=0.0)
        templates = extractor.make_dataset(takes_per_phrase=2)
        recognizer = TemplateDTWRecognizer(templates, vocabulary=vocabulary)
        sample = extractor.make_sequence(phrase_id="NEED_INTERPRETER", take_id="take-099")
        candidates = recognizer.recognize(sample)

        emission = RecognitionEventEmitter().emit(
            candidates,
            session_id="demo-001",
            utterance_id="u-test",
            t_ms=1234,
        )

        self.assertIsNone(emission.fallback_reason)
        self.assertEqual([event["type"] for event in emission.events], ["recognition.partial", "recognition.final"])
        self.assertEqual(emission.final_event["tokens"], ["INTERPRETER", "NEEDED"])

    def test_low_confidence_uses_fallback_without_final_event(self) -> None:
        candidate = RecognitionCandidate(
            phrase_id="THANK_YOU",
            tokens=("THANK_YOU",),
            label="Thank you",
            distance=0.4,
            confidence=0.65,
            rank=1,
        )

        emission = RecognitionEventEmitter(config=RecognizerConfig()).emit(
            [candidate],
            session_id="demo-001",
            utterance_id="u-low",
            t_ms=100,
        )

        self.assertEqual(emission.fallback_reason, "needs_confirmation_or_fallback_clip")
        self.assertIsNone(emission.final_event)


if __name__ == "__main__":
    unittest.main()
