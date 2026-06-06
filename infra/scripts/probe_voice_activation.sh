#!/usr/bin/env bash
set -u

ALLOW_NETWORK="${VOICE_PROBE_ALLOW_NETWORK:-false}"
PRIVATE_BASE_URL="${ELEVENLABS_PRIVATE_BASE_URL:-}"

echo "Signbridge voice activation discovery"
echo "Diagnosis order: official activation, entitlement/discovery, install state, runtime probe, app integration."
echo ""

echo "Configured providers:"
echo "- ASR_PROVIDER=${ASR_PROVIDER:-unset}"
echo "- TTS_PROVIDER=${TTS_PROVIDER:-unset}"
echo "- ELEVENLABS_ON_DEVICE_AVAILABLE=${ELEVENLABS_ON_DEVICE_AVAILABLE:-unset}"
echo "- ELEVENLABS_PRIVATE_BASE_URL=${PRIVATE_BASE_URL:-unset}"
if [ -n "${ELEVENLABS_API_KEY:-}" ]; then
  echo "- ELEVENLABS_API_KEY=set"
else
  echo "- ELEVENLABS_API_KEY=unset"
fi
echo ""

if [ "${ELEVENLABS_ON_DEVICE_AVAILABLE:-false}" = "true" ]; then
  if [ -z "$PRIVATE_BASE_URL" ]; then
    echo "BLOCKED: ELEVENLABS_ON_DEVICE_AVAILABLE=true but ELEVENLABS_PRIVATE_BASE_URL is unset." >&2
    exit 1
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "BLOCKED: curl is required to probe the private ElevenLabs endpoint." >&2
    exit 2
  fi

  echo "Probing ElevenLabs private/on-device endpoint..."
  if curl -fsS --max-time 10 "${PRIVATE_BASE_URL%/}/v1/models"; then
    echo ""
    echo "ElevenLabs private/on-device discovery probe passed."
    exit 0
  fi

  echo ""
  echo "BLOCKED: private/on-device endpoint did not respond. Re-check sponsor activation and deployment artifact before runtime debugging." >&2
  exit 1
fi

if [ "$ALLOW_NETWORK" = "true" ] && [ -n "${ELEVENLABS_API_KEY:-}" ]; then
  if ! command -v curl >/dev/null 2>&1; then
    echo "BLOCKED: curl is required to probe the public ElevenLabs API." >&2
    exit 2
  fi

  echo "Probing public ElevenLabs API because VOICE_PROBE_ALLOW_NETWORK=true..."
  if curl -fsS --max-time 10 \
    -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
    "https://api.elevenlabs.io/v1/models"; then
    echo ""
    echo "Public ElevenLabs API key works. This is sponsor-quality/cloud mode only, not offline proof."
    exit 0
  fi

  echo ""
  echo "BLOCKED: public ElevenLabs API probe failed. Check account/key activation before app debugging." >&2
  exit 1
fi

echo "ElevenLabs on-device/private is not activated in this environment."
echo "Checking local fallback candidates..."

missing=0
for cmd in piper kokoro espeak-ng whisper-cli faster-whisper; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "- $cmd: present at $(command -v "$cmd")"
  else
    echo "- $cmd: missing"
    missing=$((missing + 1))
  fi
done

echo ""
echo "Decision: use the documented local/canned fallback path unless official ElevenLabs private activation is completed."
if [ "$missing" -ge 5 ]; then
  echo "BLOCKED: no local ASR/TTS fallback command was found. Install/select fallback before offline proof." >&2
  exit 1
fi
