# ElevenLabs Activation Checklist

Last checked: 2026-06-06.

Signbridge should use ElevenLabs only after the relevant official activation path is real. A public API key is useful for sponsor-quality online mode, but it is not evidence of on-device/private deployment.

Official source anchors:

- ElevenLabs models: https://elevenlabs.io/docs/models
- ElevenLabs private deployment: https://elevenlabs.io/docs/eleven-api/private-deployment/overview
- ElevenLabs Scribe v2 Realtime docs/blog entry: https://elevenlabs.io/blog/introducing-scribe-v2-realtime

## Activation States

Use one of these states in notes and env:

- `unavailable`: no account, no entitlement, or no official private/on-device path.
- `api_only`: public API key works; valid for online sponsor-quality mode only.
- `private_pending`: sponsor says private/on-device is coming, but no endpoint or artifact has been tested.
- `private_activated`: private/on-device deployment is installed, local/private endpoint responds, and TTS/ASR probes pass.

Only `private_activated` can be used for the offline proof.

## Layered Checklist

### 1. Registration And Entitlement

- Confirm team ElevenLabs account owner.
- Confirm event sponsor instructions or account-team contact.
- Confirm whether private deployment docs/resources are visible to the team.
- Confirm which products are enabled: TTS, Scribe v2 Realtime, Agents Platform, or other.
- Confirm whether deployment is public API, private cloud, on-prem, or on-device.
- Record non-secret deployment identifiers in private team notes.

Blocker language:

> ElevenLabs on-device is blocked at registration/entitlement. Public API access exists/does not exist, but private deployment docs/artifacts are not visible. Fallback selected: local ASR/TTS.

### 2. Discovery

- Identify the endpoint shape: public API, private base URL, local LAN service, container, SDK, or binary.
- Identify required secrets and where they are injected.
- Identify required ports and whether the service can bind to LAN or localhost.
- Identify model IDs for TTS and ASR.
- Identify any license or data-residency condition relevant to demo claims.

Expected env after discovery:

```bash
ELEVENLABS_ON_DEVICE_AVAILABLE=false|true
ELEVENLABS_PRIVATE_BASE_URL=http://<local-or-private-host>:<port>
ELEVENLABS_TTS_MODEL=eleven_flash_v2_5
ELEVENLABS_ASR_MODEL=scribe_v2_realtime
```

### 3. Install State

- Confirm private/on-device artifact exists locally.
- Confirm any container image is pulled before offline mode.
- Confirm any model cache is populated before offline mode.
- Confirm endpoint starts without public egress if claiming on-device/private local proof.
- Confirm local audio input/output devices are visible to the voice service.

### 4. Runtime Probe

Run:

```bash
infra/scripts/probe_voice_activation.sh
```

For private/on-device mode, this must probe `ELEVENLABS_PRIVATE_BASE_URL`. For public API mode, set `VOICE_PROBE_ALLOW_NETWORK=true` only while online:

```bash
VOICE_PROBE_ALLOW_NETWORK=true infra/scripts/probe_voice_activation.sh
```

Public API success should be labelled `api_only`, not `private_activated`.

### 5. Demo Mode Selection

- `private_activated`: use `ASR_PROVIDER=elevenlabs_on_device` and `TTS_PROVIDER=elevenlabs_on_device`.
- `api_only`: optional online sponsor-quality voice demo; offline proof must switch to local fallback.
- `private_pending` or `unavailable`: use local fallback immediately.

## Required Proofs Before Claiming ElevenLabs On-Device

- TTS speaks a short phrase from the local/private endpoint.
- Scribe or STT path transcribes a short microphone sample from the local/private endpoint.
- Public internet can be disabled and the same voice path still works.
- The operator can show env/status without exposing secrets.
- The UI/status copy does not imply certified interpretation or general BSL translation.

## Blockers To Document Precisely

- Private docs not visible.
- Sponsor/account-team approval pending.
- Deployment artifact unavailable.
- Container/image pull requires network and has not been cached.
- Endpoint starts but does not expose TTS.
- Endpoint starts but does not expose Scribe v2 Realtime.
- Endpoint works only through public API.
- Endpoint requires public egress during inference.

If any of these are true, choose the fallback tree in `docs/runtime/ELEVENLABS_FALLBACK_DECISION_TREE.md`.
