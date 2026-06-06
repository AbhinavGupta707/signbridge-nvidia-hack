# Signbridge

Signbridge is a local-first accessibility demo built for the NVIDIA Hack for Impact London hackathon.

It helps a Deaf British Sign Language user take part in a public-services appointment when a human interpreter is not available. The demo focuses on one realistic scenario: reporting damp and mould in City of London housing.

The goal is not to replace qualified interpreters. Signbridge is designed as an assistive bridge: it recognises a small set of appointment-specific signed phrases, turns them into spoken English, captions the professional's reply, and creates a source-backed record of useful next steps.

## What It Does

- Recognises constrained housing-repair sign intents from camera landmark data.
- Translates recognised sign intent into clear English.
- Produces spoken output for the professional.
- Captions spoken replies back to the Deaf user.
- Shows source-backed policy cards and suggested questions.
- Exports an appointment record with citations, evidence prompts, and safety notes.
- Runs in a local-first way, designed for NVIDIA DGX Spark or HP ZGX Nano hardware.

## Why It Matters

Public-service appointments often involve high-stakes details: repairs, health risks, deadlines, complaints, and evidence. If communication access fails, people can leave without a clear record or the right follow-up questions.

Signbridge gives the user a safer appointment loop:

1. Sign the issue.
2. Confirm the recognised meaning.
3. Speak it out loud.
4. Read the professional's reply as captions.
5. See relevant source-backed prompts.
6. Leave with a record.

## Current Status

This repo contains a complete pre-hardware integration baseline.

Working today on a normal laptop:

- Shared event contracts.
- FastAPI WebSocket orchestrator.
- Web demo interface.
- Mock replay mode.
- Hybrid local mode with synthetic recognition, voice provider boundaries, source-backed advocacy, and citation-backed record export.
- Validation scripts and demo runbooks.

Still requiring DGX Spark/ZGX Nano hardware:

- GPU/runtime proof.
- Local model runtime selection through NIM, Ollama, or llama.cpp.
- Real camera and MediaPipe performance checks.
- Real sign-clip landmark extraction.
- Actual constrained recogniser validation on consented clips.
- Offline proof on the event hardware.

## Run Locally

Install Python dependencies if needed:

```bash
python3 -m pip install -r services/orchestrator/requirements.txt
```

Run the full pre-hardware check:

```bash
make prehardware-check
```

Start the highest-fidelity local backend:

```bash
make dev-hybrid
```

In another terminal, start the web app:

```bash
cd apps/web
npm run start
```

Open:

```text
http://127.0.0.1:5173/?ws=ws://127.0.0.1:8000/ws
```

Useful backend endpoints:

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/mock/events`
- `GET http://127.0.0.1:8000/mock/records/{session_id}.html`
- `GET http://127.0.0.1:8000/mock/records/{session_id}.json`
- `WS ws://127.0.0.1:8000/ws`

## Demo Modes

Mock mode:

```bash
make dev
```

This uses deterministic placeholder providers and is useful for frontend replay.

Hybrid mode:

```bash
make dev-hybrid
```

This is the main pre-hardware mode. Recognition is still synthetic, but the rest of the flow uses the real local service boundaries where possible: voice provider interfaces, source-backed advocacy, and record export.

## Repository Guide

- `apps/web` - live session web interface.
- `services/orchestrator` - FastAPI WebSocket event bus.
- `services/vision` - constrained sign-recognition scaffold.
- `services/voice` - translation, ASR, and TTS provider interfaces.
- `services/advocacy` - local retrieval, policy cards, question prompts, and record export.
- `packages/contracts` - shared event schemas and validation.
- `infra` - runtime and hardware probe scripts.
- `demo` - runbooks, pitch material, fallback plans, and offline proof notes.
- `docs` - implementation plans, research notes, and hardware readiness docs.

## Important Docs

- [Product specification](signbridge-product-spec.md)
- [Implementation plan](IMPLEMENTATION_PLAN.md)
- [Pre-hardware readiness](docs/PRE_HARDWARE_READINESS.md)
- [Runtime checklist](docs/runtime/DGX_SPARK_ZGX_NANO_CHECKLIST.md)
- [Offline proof runbook](demo/OFFLINE_PROOF.md)
- [Open flags](docs/OPEN_FLAGS.md)

## Safety Position

Signbridge should be presented as a constrained assistive tool, not a general BSL translator and not legal advice.

Policy cards are source-backed prompts for discussion and record keeping. A human should confirm the meaning before speech output, and qualified interpreters remain the right standard for real public-service access.
