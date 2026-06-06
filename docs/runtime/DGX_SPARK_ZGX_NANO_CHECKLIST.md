# DGX Spark / HP ZGX Nano Runtime Checklist

Last checked: 2026-06-06.

This checklist prepares Signbridge for NVIDIA DGX Spark or HP ZGX Nano G1n AI Station. It follows the project diagnosis rule: if a capability is missing or unavailable, first check registration, discovery, install state, and official activation flows. Only debug permissions or runtime behavior after the capability is actually present.

## Source Anchors

- NVIDIA DGX Spark local network access: https://build.nvidia.com/spark/connect-to-your-spark/overview
- NVIDIA DGX Spark dashboard: https://build.nvidia.com/spark/dgx-dashboard/overview
- NVIDIA NIM on Spark: https://build.nvidia.com/spark/nim-llm
- NVIDIA llama.cpp on Spark: https://build.nvidia.com/spark/llama-cpp
- NVIDIA Ollama playbooks on Spark: https://build.nvidia.com/spark
- HP ZGX Nano G1n specs: https://support.hp.com/us-en/document/ish_13212147-13212192-16

## Layer 0: Assignment And Activation

- Confirm which physical target is assigned: `dgx_spark`, `zgx_nano`, or laptop-only fallback.
- Record hostname, mDNS name, LAN IP, admin user, and team SSH user in the private team notes, not in git.
- Complete the official first-run device setup before any runtime debugging.
- Confirm the laptop and device are on the same LAN or connected through the official NVIDIA Sync/manual SSH path.
- Confirm NGC account access and NGC API key if using NIM.
- Confirm ElevenLabs event/sponsor account and whether private/on-device resources are actually visible.
- If anyone says "Codex Spark", confirm whether they mean NVIDIA DGX Spark.

## Layer 1: Hardware Discovery

Run:

```bash
infra/scripts/runtime_inventory.sh
```

Expected DGX Spark / ZGX Nano signals:

- OS: NVIDIA DGX OS on Ubuntu 24.04 family.
- Architecture: Arm64/aarch64 is expected for GB10 systems.
- GPU: NVIDIA Grace Blackwell / GB10 visible through `nvidia-smi`.
- Memory: 128 GB unified memory class.
- Storage: enough free space for model weights, local policy corpus, demo clips, and cache. Reserve at least 80 GB if testing multiple LLM runtimes.
- Network: stable LAN IP reachable from the web client laptop.

If `nvidia-smi` is missing, stop and check official device setup/registration first. Do not start CUDA permission debugging until the device and NVIDIA stack are confirmed installed.

## Layer 2: Install State

Required for all paths:

- `curl`
- `git`
- `python3`
- LAN access from client laptop to orchestrator and model server

Required for NIM:

- Docker
- NVIDIA Container Toolkit
- NGC account and API key
- NIM container entitlement and image availability

Required for Ollama:

- Ollama installed from the official path or NVIDIA Spark playbook
- A downloaded local model
- GPU discovery confirmed in Ollama logs or through runtime behavior

Required for llama.cpp:

- `git`
- `cmake`
- CUDA toolkit with `nvcc`
- Built `llama-server`
- Downloaded GGUF model file

Required for voice fallback:

- At least one TTS fallback: `piper`, `kokoro`, `espeak-ng`, or approved canned audio
- At least one ASR fallback: `whisper-cli`, `faster-whisper`, typed captions, or approved canned reverse path

## Layer 3: Runtime Probes

Local LLM:

```bash
infra/scripts/probe_llm_runtime.sh "$LLM_BASE_URL" "$LLM_MODEL"
```

Voice activation:

```bash
infra/scripts/probe_voice_activation.sh
```

Offline readiness:

```bash
infra/scripts/offline_preflight.sh
```

The LLM probe must return a completion from a local or LAN endpoint before the demo can claim local inference. Public cloud API success is useful for development but does not satisfy the offline proof.

## Layer 4: Offline Proof Gate

Before judge-facing offline proof:

- `OFFLINE_MODE=true`
- `ALLOW_NETWORK_EGRESS=false`
- `LLM_BASE_URL` points to localhost, `.local`, or RFC1918 LAN.
- `ASR_PROVIDER` is local/on-device/canned/typed, not `elevenlabs_api`.
- `TTS_PROVIDER` is local/on-device/canned, not `elevenlabs_api`.
- Public data corpus and model weights are already downloaded.
- Public egress is physically or administratively disabled after startup, then the demo path still works.

## Blocker Log Template

Use this exact shape in PRs or standup notes:

```md
## Runtime Blocker

- Capability:
- Layer reached: registration | discovery | install | runtime | permissions
- Evidence:
- Official flow checked:
- Current state:
- Demo impact:
- Fallback selected:
- Owner:
- Next check time:
```

Examples:

- Capability: ElevenLabs on-device TTS. Layer reached: registration. Evidence: public API key exists, private deployment docs not visible. Fallback selected: Piper/espeak-ng local TTS. Do not debug provider code yet.
- Capability: NIM LLM. Layer reached: install. Evidence: NGC key present, Docker present, `docker run --gpus all ... nvidia-smi` fails. Fallback selected: llama.cpp or Ollama after their official discovery passes.
