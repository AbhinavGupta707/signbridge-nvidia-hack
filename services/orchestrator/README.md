# Orchestrator

FastAPI and WebSocket event bus lives here.

This is a mock-only integration scaffold. It creates the backend shell that other branches can target before real providers exist.

Implemented endpoints:

- `GET /health` returns orchestrator and mock component status.
- `GET /mock/events` returns the scripted server events from `packages/contracts/examples/scripted_demo.server.events.json`.
- `GET /mock/records/{session_id}.html` returns an in-memory mock record.
- `WS /ws` accepts contract events and returns mock server events.

## Run

From the repo root:

```bash
make dev
```

The default server is `http://127.0.0.1:8000`.

## WebSocket Replay

Connect a frontend to:

```text
ws://127.0.0.1:8000/ws?replay=scripted
```

Or send:

```json
{"type":"demo.replay","session_id":"demo-001","scenario":"housing_repair"}
```

The replay emits `system.status`, `recognition.*`, `translation.final`, `tts.audio`, `caption.*`, `policy.card`, `question.prompt`, `record.updated`, and `record.exported`.

## Mock Boundaries

These providers are intentionally fake:

- recognition: scripted constrained-vocabulary tokens
- translation: deterministic templates
- TTS: placeholder base64 audio envelope
- captions: scripted professional response
- policy cards: placeholder source metadata, no RAG
- question prompts: scripted prompt text
- record updates: in-memory only

Do not add real vision, voice, advocacy retrieval, or frontend internals in this branch.
