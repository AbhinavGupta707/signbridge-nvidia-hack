# Landmark Data Format

Signbridge stores extracted landmarks as JSONL: one completed phrase clip per line. This keeps the demo data inspectable, streamable, and easy to convert to `.npz` later if needed.

Minimal sequence object:

```json
{
  "clip_id": "housing-DAMP_IN_HOME-s01-t01",
  "phrase_id": "DAMP_IN_HOME",
  "signer_id": "s01-consented",
  "take_id": "t01",
  "scenario": "housing_repair",
  "tokens": ["DAMP", "MY_HOME"],
  "landmarks_version": "mediapipe_holistic_v1",
  "source_clip_path": "data/sign_clips/local/housing-DAMP_IN_HOME-s01-t01.mp4",
  "frames": [
    {
      "frame_index": 0,
      "t_ms": 0,
      "points": [
        {"landmark_set": "pose", "index": 11, "x": 0.42, "y": 0.42, "z": 0.0, "visibility": 0.99},
        {"landmark_set": "right_hand", "index": 8, "x": 0.66, "y": 0.48, "z": 0.0, "visibility": 0.98}
      ]
    }
  ],
  "metadata": {
    "extractor": "mediapipe_holistic",
    "include_face": false
  }
}
```

Point rules:

- `landmark_set` is normally `pose`, `left_hand`, or `right_hand`. Face landmarks are optional and off by default for compact demo data.
- Coordinates are MediaPipe-normalized image coordinates. The recognizer performs per-frame centering and scale normalization before matching.
- Missing or low-visibility points are allowed. The vectorizer fills missing points with zeros after normalization.
- Do not store raw image frames in landmark files.

Evaluation target for the hackathon demo: at least 10 scripted phrases at 80%+ top-1 accuracy in demo lighting, or a clear confidence fallback instead of speaking an uncertain result.

