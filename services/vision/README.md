# Vision

Landmark extraction and constrained sign recognition lives here for the housing repair / damp and mould demo. This subsystem recognises a fixed phrase vocabulary only. It must not be described as general BSL translation or certified interpretation.

## Scope

- Vocabulary: 25 housing-repair phrases in `vocabulary/housing_repair_vocabulary.json`.
- Input: completed local sign clips or camera segments converted to MediaPipe-style landmarks.
- Baseline recogniser: template matching with DTW by default, nearest centroid available for comparison.
- Output: shared-contract `recognition.partial` and `recognition.final` events.
- Fallback: low-confidence results do not produce final recognition events.

## Data Flow

```text
local clip/camera segment
  -> MediaPipeHolisticExtractor or MockLandmarkExtractor
  -> LandmarkSequence JSONL
  -> TemplateDTWRecognizer
  -> RecognitionEventEmitter
  -> recognition.partial / recognition.final
```

Raw video is not required at inference time. The demo should prefer extracted landmarks or approved fallback clips unless a live camera path is actively being tested.

## Clip And Landmark Formats

- Clip manifests: `data/sign_clips/README.md`
- Landmark JSONL: `data/landmarks/README.md`

The JSONL landmark format stores one completed phrase clip per line. It includes `phrase_id`, `tokens`, signer/take metadata, `landmarks_version`, and frame-level landmark points. It stores no raw image frames.

## Optional MediaPipe Extraction

MediaPipe and OpenCV are optional. If they are unavailable, the mock extractor and fixture evaluation still run.

```bash
python3 -m services.vision.scripts.extract_landmarks \
  data/sign_clips/housing_manifest.jsonl \
  data/landmarks/housing_repair_landmarks.jsonl
```

If the command reports missing `mediapipe` or `opencv-python`, check install/discovery state first, then use `MockLandmarkExtractor` for offline smoke tests until the camera stack is present.

## Evaluate

Synthetic smoke test:

```bash
python3 -m services.vision.scripts.evaluate_recognizer --use-mock-fixture
```

Real extracted data:

```bash
python3 -m services.vision.scripts.evaluate_recognizer data/landmarks/housing_repair_landmarks.jsonl
```

Report the following in validation notes:

- top-1 accuracy
- accepted accuracy at the final confidence threshold
- fallback/reject count
- phrase confusions
- signer/data limitations

Hackathon target: recognise at least 10 scripted phrases at 80%+ top-1 accuracy in demo conditions, or clearly fall back before any speech is produced.

## Confidence Policy

- `confidence >= 0.72`: emit `recognition.partial`, then `recognition.final`.
- `0.55 <= confidence < 0.72`: emit `recognition.partial`, require confirmation or use an approved fallback clip.
- `confidence < 0.55`: emit no recognition event; retry or use fallback.

Downstream systems should only speak or translate after `recognition.final` or after an explicit user correction/confirmation.
