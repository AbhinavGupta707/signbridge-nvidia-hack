# Infrastructure

Runtime and deployment notes live here.

Initial target:

- DGX Spark or HP ZGX Nano discovery.
- NVIDIA runtime and local model serving activation.
- ElevenLabs access discovery.
- Offline proof runbook.

## Runtime Pack

Scripts:

- `infra/scripts/runtime_inventory.sh` writes a read-only discovery report for hardware, CUDA, containers, model runtimes, voice providers, and LAN state.
- `infra/scripts/probe_llm_runtime.sh` validates the selected OpenAI-compatible local LLM endpoint.
- `infra/scripts/probe_voice_activation.sh` checks ElevenLabs activation state and local fallback availability.
- `infra/scripts/offline_preflight.sh` validates that the selected providers are eligible for offline proof.

Docs:

- `docs/runtime/DGX_SPARK_ZGX_NANO_CHECKLIST.md`
- `docs/runtime/MODEL_RUNTIME_DISCOVERY.md`
- `docs/runtime/ELEVENLABS_ACTIVATION.md`
- `docs/runtime/ELEVENLABS_FALLBACK_DECISION_TREE.md`
- `docs/runtime/ENVIRONMENT.md`
- `demo/OFFLINE_PROOF.md`

These materials intentionally follow the project diagnosis order: registration and official activation first, then discovery, install state, runtime probes, and only then permissions/debugging.
