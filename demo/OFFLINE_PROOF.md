# Offline Proof Runbook

Purpose: prove that Signbridge's core demo path can run without inference-time public internet. This is not a generic security audit; it is a judge-facing local-first proof for the constrained public-service demo.

## Pass Criteria

- Local/LAN web client reaches the orchestrator.
- Local/LAN LLM endpoint returns a prompt response.
- Sign-to-English path works through live, prerecorded, precomputed, or scripted recognition.
- TTS speaks through on-device/private ElevenLabs or a labelled local fallback.
- Professional speech captions work through on-device/private ElevenLabs, local ASR, or a labelled typed/canned fallback.
- Policy/question/record path uses local cached sources.
- Public egress is disabled and the selected path still works.

## Before The Event

- Download model weights and voice assets.
- Cache City of London/London public-service source documents.
- Cache NIM/Ollama/llama.cpp container/image/model assets for the selected runtime.
- Record approved fallback clips and any canned voice/caption assets.
- Save the selected provider state in `.env`.
- Run all probes once while online, then again with public egress disabled.

## Setup

```bash
set -a
source .env
set +a
infra/scripts/runtime_inventory.sh
infra/scripts/probe_llm_runtime.sh "$LLM_BASE_URL" "$LLM_MODEL"
infra/scripts/probe_voice_activation.sh
```

If any capability is missing, stop at the layer where it is missing. Do not debug app code until registration, discovery, install state, and official activation are confirmed.

## Offline Configuration

Required:

```bash
OFFLINE_MODE=true
ALLOW_NETWORK_EGRESS=false
```

Valid offline LLM providers:

- `nim`, if NIM is already running locally or on LAN and model assets are cached.
- `ollama`, if model is downloaded and endpoint is local/LAN.
- `llama_cpp`, if GGUF is local and `llama-server` is running locally/LAN.
- `local_openai`, if it is genuinely local/LAN.

Invalid offline LLM provider:

- Any public cloud endpoint.

Valid offline voice providers:

- `elevenlabs_on_device`, only after private/on-device activation and local/private probe.
- `piper`, `kokoro`, `espeak_ng`, `whisper_cpp`, `faster_whisper`.
- `typed` or `canned`, if clearly labelled as fallback.

Invalid offline voice providers:

- `elevenlabs_api`.

## Disabling Public Egress

Preferred proof order:

1. Keep LAN between client and runtime device active.
2. Disable WAN/public internet at router, venue network, or device firewall.
3. Avoid disabling the local LAN needed by the browser and runtime.
4. Run:

```bash
infra/scripts/offline_preflight.sh
```

The preflight verifies selected providers and local/LAN URLs. It does not itself disable the internet.

## Demo Steps

1. Show the runtime inventory report timestamp and selected providers.
2. Show `OFFLINE_MODE=true` and `ALLOW_NETWORK_EGRESS=false` without revealing secrets.
3. Run the LLM probe or show its latest output.
4. Run one constrained signed phrase through the best available recognition path.
5. Confirm the English sentence is spoken through the selected TTS path.
6. Capture or type one professional response and show captions.
7. Show one citation-backed policy card from cached sources.
8. Export or update the appointment record.
9. State the limitation: constrained vocabulary, not certified interpretation, production requires Deaf-led co-design.

## Fallback Ladder

1. Live camera recognition.
2. Prerecorded signing clips through the recogniser.
3. Precomputed landmark files through the recogniser.
4. Scripted contract-compliant event replay through orchestrator.
5. UI-only walkthrough, clearly labelled as not the offline inference proof.

Voice fallback:

1. ElevenLabs private/on-device if officially activated and offline-proven.
2. Local TTS/ASR.
3. Typed/canned reverse path, clearly labelled.
4. No voice claim.

## Evidence To Keep

- Runtime inventory report.
- LLM probe output.
- Voice activation probe output.
- Offline preflight output.
- Screenshot or photo of disabled public egress if practical.
- Exported record from the offline run.

## Failure Language

Use precise, calm language:

> ElevenLabs on-device was not available through the official activation path, so this offline proof uses a local voice fallback. The provider boundary is unchanged.

> NIM entitlement was not available, so the local model is served through Ollama/llama.cpp for the proof.

Avoid:

- Claiming public API calls are offline.
- Claiming typed/canned captions are live ASR.
- Claiming general BSL translation.
