# ElevenLabs On-Device Fallback Decision Tree

Use this when ElevenLabs on-device/private deployment is unavailable, pending, or not yet proven offline.

## Decision Tree

```text
Need Signbridge voice path
|
+-- Is ElevenLabs private/on-device officially activated?
|   |
|   +-- No --> Mark state unavailable/private_pending.
|   |          Use local/canned fallback for offline proof.
|   |
|   +-- Yes
|       |
|       +-- Does local/private endpoint respond to TTS and ASR probes?
|           |
|           +-- No --> Do not debug app code yet.
|           |          Re-check endpoint, artifact, model cache, and sponsor docs.
|           |          Use local/canned fallback.
|           |
|           +-- Yes
|               |
|               +-- Does it work with public egress disabled?
|                   |
|                   +-- Yes --> Use elevenlabs_on_device for offline proof.
|                   |
|                   +-- No --> Treat as online-only.
|                              Use local/canned fallback for offline proof.
```

## Fallback Ranking

For Signbridge, reliability and honesty beat voice quality.

### TTS

1. `piper`: local neural TTS if installed and voice model cached.
2. `kokoro`: local TTS if installed, cached, and stable on the target.
3. `espeak_ng`: deterministic local speech. Lower quality, but excellent proof of no cloud dependency.
4. `canned`: pre-rendered approved phrases generated before offline mode, clearly labelled.
5. `mock`: UI/status plumbing only. Do not claim spoken local TTS.

### ASR

1. `whisper_cpp`: local ASR if installed and model cached.
2. `faster_whisper`: local ASR if installed and model cached.
3. `typed`: operator types the professional response, clearly labelled as reverse-path fallback.
4. `canned`: replay approved caption events, clearly labelled.
5. `mock`: UI/status plumbing only. Do not claim live local ASR.

## Env Choices

Offline with local TTS and local ASR:

```bash
OFFLINE_MODE=true
ALLOW_NETWORK_EGRESS=false
ASR_PROVIDER=whisper_cpp
TTS_PROVIDER=piper
ELEVENLABS_ON_DEVICE_AVAILABLE=false
```

Offline with typed/canned reverse path:

```bash
OFFLINE_MODE=true
ALLOW_NETWORK_EGRESS=false
ASR_PROVIDER=typed
TTS_PROVIDER=espeak_ng
ELEVENLABS_ON_DEVICE_AVAILABLE=false
```

Online sponsor-quality mode only:

```bash
OFFLINE_MODE=false
ALLOW_NETWORK_EGRESS=true
ASR_PROVIDER=elevenlabs_api
TTS_PROVIDER=elevenlabs_api
ELEVENLABS_ON_DEVICE_AVAILABLE=false
```

## Judge-Facing Language

Use:

> ElevenLabs on-device/private deployment was not available through the official activation path, so the offline proof uses a local voice fallback. The architecture keeps the same provider boundary and can switch to ElevenLabs on-device when entitlement is active.

Avoid:

- "ElevenLabs is running on-device" unless the private/local endpoint passed offline proof.
- "Live ASR" if the path is typed or canned.
- "General BSL translation" in any fallback mode.

## Blocker Output

```md
## ElevenLabs Fallback Decision

- Activation state:
- Last official flow checked:
- Probe command:
- Probe result:
- Selected ASR fallback:
- Selected TTS fallback:
- Offline proof eligible:
- Judge-facing label:
```
