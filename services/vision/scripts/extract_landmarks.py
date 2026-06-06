"""Extract MediaPipe landmarks from a local sign-clip manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from services.vision.signbridge_vision.data import write_landmark_jsonl
from services.vision.signbridge_vision.extractors import MediaPipeHolisticExtractor, MissingVisionDependency
from services.vision.signbridge_vision.vocabulary import load_housing_repair_vocabulary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="JSONL manifest in data/sign_clips format.")
    parser.add_argument("output", type=Path, help="Output landmark JSONL path.")
    parser.add_argument("--include-face", action="store_true", help="Include face landmarks. Off by default for compact demo data.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vocabulary = load_housing_repair_vocabulary()
    extractor = MediaPipeHolisticExtractor(include_face=args.include_face)
    sequences = []

    try:
        for clip in load_manifest(args.manifest):
            phrase_id = clip["phrase_id"]
            entry = vocabulary.get(phrase_id)
            sequences.append(
                extractor.extract_clip(
                    Path(clip["clip_path"]),
                    clip_id=clip["clip_id"],
                    phrase_id=phrase_id,
                    signer_id=clip["signer_id"],
                    take_id=clip["take_id"],
                    tokens=entry.tokens,
                )
            )
    except MissingVisionDependency as exc:
        raise SystemExit(str(exc)) from exc

    write_landmark_jsonl(args.output, sequences)
    print(f"Wrote {len(sequences)} landmark sequence(s) to {args.output}")
    return 0


def load_manifest(path: Path) -> list[dict[str, str]]:
    clips: list[dict[str, str]] = []
    required = {"clip_id", "phrase_id", "signer_id", "take_id", "clip_path"}
    with path.open("r", encoding="utf-8") as manifest_file:
        for line_number, line in enumerate(manifest_file, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            payload = json.loads(stripped)
            missing = required - set(payload)
            if missing:
                raise ValueError(f"{path}:{line_number}: missing fields: {', '.join(sorted(missing))}")
            clips.append({key: str(payload[key]) for key in required})
    return clips


if __name__ == "__main__":
    raise SystemExit(main())

