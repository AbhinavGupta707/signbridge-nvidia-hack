# Orchestrator

FastAPI and WebSocket event bus lives here.

This service supports two local modes:

- `mock`: deterministic replay and placeholder providers for frontend wiring.
- `hybrid`: synthetic recognition plus local voice provider boundaries, source-backed advocacy agents, and citation-backed record export. This is the best pre-hardware integration mode.

Implemented endpoints:

- `GET /health` returns orchestrator and component status.
- `GET /mock/events` returns the scripted server events from `packages/contracts/examples/scripted_demo.server.events.json`.
- `GET /mock/records/{session_id}.html` returns an in-memory mock or hybrid record.
- `GET /mock/records/{session_id}.json` returns the same record as JSON.
- `WS /ws` accepts contract events and returns server events.

## Run

From the repo root:

```bash
make dev
```

The default server is `http://127.0.0.1:8000`.

For pre-hardware integration:

```bash
make dev-hybrid
```

Or explicitly:

```bash
SIGNBRIDGE_ORCHESTRATOR_MODE=hybrid python3 -m uvicorn services.orchestrator.app:app --host 127.0.0.1 --port 8000
```

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

## Mode Boundaries

In `mock` mode these providers are intentionally fake:

- recognition: scripted constrained-vocabulary tokens
- translation: deterministic templates
- TTS: placeholder base64 audio envelope
- captions: scripted professional response
- policy cards: placeholder source metadata, no RAG
- question prompts: scripted prompt text
- record updates: in-memory only

In `hybrid` mode:

- recognition remains synthetic until clips/hardware are available
- translation/TTS/ASR use `services/voice` provider interfaces
- policy/question output uses `services/advocacy` source-backed retrieval
- record export uses the advocacy `RecordAgent`

Do not make hardware availability a precondition for local development. Keep `hybrid` mode green before swapping in real DGX/ZGX providers.
