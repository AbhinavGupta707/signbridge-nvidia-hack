# Pre-Hardware Readiness

This is the work that can be completed before DGX Spark or ZGX Nano hardware is physically available.

## What We Can Prove Now

- Shared event contracts validate.
- The mock WebSocket replay drives the frontend.
- The `hybrid` orchestrator mode runs the highest-fidelity local path available without hardware:
  - synthetic/mock recognition events
  - local voice provider boundary
  - local TTS/ASR fallback or mock output
  - source-backed advocacy policy/question events
  - citation-backed record export
- The frontend builds and can connect to the orchestrator.
- Runtime scripts can syntax-check and document what to probe tomorrow.

## What We Cannot Prove Without Hardware

- DGX Spark/ZGX Nano GPU visibility, drivers, NIM containers, Ollama GPU path, llama.cpp CUDA path.
- Actual on-device/private ElevenLabs activation.
- Real camera-to-MediaPipe performance on the demo LAN/device.
- Real sign recognition accuracy on consented clips.
- Full offline proof on the NVIDIA/HP box.

## Local Commands

Run the complete pre-hardware suite:

```bash
make prehardware-check
```

Run the mock orchestrator:

```bash
make dev
```

Run the highest-fidelity local mode:

```bash
make dev-hybrid
```

Then open the web app in another terminal:

```bash
cd apps/web
npm run start
```

Use this URL so the web app points to the default orchestrator:

```text
http://127.0.0.1:5173/?ws=ws://127.0.0.1:8000/ws
```

## Tomorrow Hardware Sequence

Follow this order on the DGX Spark/ZGX Nano:

1. Run `infra/scripts/runtime_inventory.sh`.
2. Prove local network access and browser reachability.
3. Run `infra/scripts/probe_llm_runtime.sh`.
4. Select the first working local model route: NIM, Ollama, or llama.cpp.
5. Run `infra/scripts/probe_voice_activation.sh`.
6. If ElevenLabs on-device/private is unavailable, lock local ASR/TTS fallback.
7. Run `make prehardware-check` on the hardware.
8. Run `make dev-hybrid` and connect the frontend.
9. Only then replace synthetic recognition with real clip/landmark input.

## Development Priorities Before Hardware Arrives

1. Keep `hybrid` mode green.
2. Capture or prepare the exact phrase list and consent workflow.
3. Add real clip manifests as local, ignored data.
4. Generate landmarks locally if MediaPipe/OpenCV are available on the laptop.
5. Rehearse the fallback ladder from `demo/FALLBACKS.md`.

