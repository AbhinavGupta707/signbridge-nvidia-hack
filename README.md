# Signbridge

Local-first British Sign Language to speech and speech to captions system for NVIDIA Hack for Impact London.

Signbridge is a blue-sky architecture build for a public-services appointment where a Deaf BSL user has no human interpreter available. The target demo is a constrained, honest, high-quality system: sign intent recognition from camera landmarks, local LLM fluency, spoken output, live captions, and policy/question/record agents grounded in London public data.

See:

- [Product specification](signbridge-product-spec.md)
- [Implementation plan](IMPLEMENTATION_PLAN.md)
- [Parallel agent workflow](docs/BRANCHING_AND_PARALLEL_AGENTS.md)
- [Kickoff guide](docs/KICKOFF.md)
- [Research and data checks](docs/RESEARCH_AND_DATA_CHECKS.md)
- [Open flags](docs/OPEN_FLAGS.md)
- [Runtime checklist](docs/runtime/DGX_SPARK_ZGX_NANO_CHECKLIST.md)
- [Pre-hardware readiness](docs/PRE_HARDWARE_READINESS.md)
- [Offline proof runbook](demo/OFFLINE_PROOF.md)

## Current Status

This repo now has a reconciled pre-hardware integration baseline on `integration/session-output-review`:

- shared event contracts in `packages/contracts`
- mock and hybrid FastAPI orchestrator modes in `services/orchestrator`
- `/health`, `/mock/events`, `/mock/records/{session_id}.html`, `/mock/records/{session_id}.json`, and `/ws`
- deterministic mock providers for recognition, translation, TTS, captions, policy cards, question prompts, and record updates
- hybrid local flow with synthetic recognition, activation-gated voice provider boundaries, source-backed advocacy cards/questions, and citation-backed record export

Implementation agents should work in feature branches and must respect the shared event contracts before building deeper modules.

## Local Dev

Install Python dependencies if your environment does not already have them:

```bash
python3 -m pip install -r services/orchestrator/requirements.txt
```

Validate the shared contracts and sample events:

```bash
make validate-contracts
```

Run the mock orchestrator:

```bash
make dev
```

Run the highest-fidelity local mode available before DGX/ZGX hardware:

```bash
make dev-hybrid
```

Run the full pre-hardware validation suite:

```bash
make prehardware-check
```

Then, in another terminal:

```bash
make health
make replay-smoke
```

Useful local endpoints:

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/mock/events`
- `WS ws://127.0.0.1:8000/ws`

To auto-stream the scripted demo for a frontend, connect to:

```text
ws://127.0.0.1:8000/ws?replay=scripted
```

Or send this event after connecting:

```json
{"type":"demo.replay","session_id":"demo-001","scenario":"housing_repair"}
```

## First Build Principle

Do architecture first, then quality. No shortcuts that undermine privacy, source-backed policy claims, demo reliability, or the ethical position that Signbridge augments but does not replace qualified interpreters.

## Runtime Activation

Hardware/runtime work lives under `infra/**`, `docs/runtime/**`, and `demo/OFFLINE_PROOF.md`. If NVIDIA, ElevenLabs, or another provider capability is missing, check registration, official activation, discovery, and install state before debugging permissions or app code.
