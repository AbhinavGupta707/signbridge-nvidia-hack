# Sign Clip Storage Format

This folder is for local, consented sign-clip manifests and approved demo captures. Do not commit raw video by default. Keep raw captures local unless the signer has explicitly consented to repository storage.

The vision branch expects a JSONL manifest with one clip per line:

```json
{"clip_id":"housing-DAMP_IN_HOME-s01-t01","phrase_id":"DAMP_IN_HOME","signer_id":"s01-consented","take_id":"t01","scenario":"housing_repair","clip_path":"data/sign_clips/local/housing-DAMP_IN_HOME-s01-t01.mp4","consent":{"recorded":true,"repo_storage":false},"capture":{"device":"laptop-camera","fps":30,"lighting":"demo-room"}}
```

Required fields for extraction are `clip_id`, `phrase_id`, `signer_id`, `take_id`, and `clip_path`.

Operational rules:

- The phrase id must exist in `services/vision/vocabulary/housing_repair_vocabulary.json`.
- Raw video is only an input to landmark extraction. The offline demo should run from landmarks or approved fallback clips.
- Use pseudonymous signer ids. Do not store names, contact details, or medical details here.
- If a Deaf collaborator provides data, capture explicit consent and state the allowed use. If team-member prototype data is used, label it as prototype data.

