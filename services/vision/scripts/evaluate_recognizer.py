"""Evaluate the constrained landmark recognizer."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from services.vision.signbridge_vision.data import LandmarkSequence, load_landmark_jsonl
from services.vision.signbridge_vision.extractors import MockLandmarkExtractor
from services.vision.signbridge_vision.recognizer import RecognizerConfig, TemplateDTWRecognizer
from services.vision.signbridge_vision.vocabulary import load_housing_repair_vocabulary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", nargs="?", type=Path, help="Landmark JSONL file. One sequence per line.")
    parser.add_argument(
        "--use-mock-fixture",
        action="store_true",
        help="Evaluate deterministic synthetic landmarks when real extracted data is unavailable.",
    )
    parser.add_argument("--method", choices=("dtw", "centroid"), default="dtw")
    parser.add_argument("--takes-per-phrase", type=int, default=4)
    parser.add_argument("--min-confidence", type=float, default=0.72)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vocabulary = load_housing_repair_vocabulary()
    sequences = load_sequences(args, vocabulary)
    if len(sequences) < 2:
        raise SystemExit("Need at least two landmark sequences for evaluation")

    config = RecognizerConfig(method=args.method, final_threshold=args.min_confidence)
    results = leave_one_out(sequences, vocabulary, config)
    print_report(results, min_confidence=args.min_confidence, method=args.method)
    return 0


def load_sequences(args: argparse.Namespace, vocabulary) -> list[LandmarkSequence]:
    if args.use_mock_fixture:
        return MockLandmarkExtractor(vocabulary=vocabulary, noise=0.003).make_dataset(
            takes_per_phrase=args.takes_per_phrase
        )
    if not args.dataset:
        raise SystemExit("Pass a landmark JSONL dataset or --use-mock-fixture")
    return load_landmark_jsonl(args.dataset)


def leave_one_out(sequences: list[LandmarkSequence], vocabulary, config: RecognizerConfig) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for index, test_sequence in enumerate(sequences):
        train_sequences = [
            sequence
            for train_index, sequence in enumerate(sequences)
            if train_index != index and sequence.phrase_id != test_sequence.phrase_id
        ]
        train_sequences.extend(
            sequence
            for train_index, sequence in enumerate(sequences)
            if train_index != index and sequence.phrase_id == test_sequence.phrase_id
        )
        if not train_sequences:
            continue

        recognizer = TemplateDTWRecognizer(train_sequences, vocabulary=vocabulary, config=config)
        candidates = recognizer.recognize(test_sequence)
        best = candidates[0]
        results.append(
            {
                "clip_id": test_sequence.clip_id,
                "expected": test_sequence.phrase_id,
                "predicted": best.phrase_id,
                "confidence": best.confidence,
                "accepted": best.confidence >= config.final_threshold,
                "correct": best.phrase_id == test_sequence.phrase_id,
            }
        )
    return results


def print_report(results: list[dict[str, object]], *, min_confidence: float, method: str) -> None:
    total = len(results)
    correct = sum(1 for result in results if result["correct"])
    accepted = [result for result in results if result["accepted"]]
    accepted_correct = sum(1 for result in accepted if result["correct"])
    rejected = total - len(accepted)

    print(f"Signbridge vision recognizer evaluation ({method})")
    print(f"Samples: {total}")
    print(f"Top-1 accuracy: {correct / total:.3f} ({correct}/{total})")
    if accepted:
        print(f"Accepted accuracy at confidence >= {min_confidence:.2f}: {accepted_correct / len(accepted):.3f} ({accepted_correct}/{len(accepted)})")
    else:
        print(f"Accepted accuracy at confidence >= {min_confidence:.2f}: n/a (0 accepted)")
    print(f"Fallback/reject count: {rejected}")

    confusion: dict[str, Counter[str]] = defaultdict(Counter)
    for result in results:
        if not result["correct"]:
            confusion[str(result["expected"])][str(result["predicted"])] += 1

    if confusion:
        print("Confusions:")
        for expected, predictions in sorted(confusion.items()):
            rendered = ", ".join(f"{predicted}={count}" for predicted, count in predictions.most_common())
            print(f"  {expected}: {rendered}")
    else:
        print("Confusions: none")


if __name__ == "__main__":
    raise SystemExit(main())

