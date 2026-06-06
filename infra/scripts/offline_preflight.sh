#!/usr/bin/env bash
set -u

failures=0
warnings=0

fail() {
  echo "BLOCKED: $*" >&2
  failures=$((failures + 1))
}

warn() {
  echo "WARN: $*" >&2
  warnings=$((warnings + 1))
}

is_localish_url() {
  local url="$1"
  case "$url" in
    http://localhost:*|http://127.*|http://0.0.0.0:*|http://10.*|http://172.16.*|http://172.17.*|http://172.18.*|http://172.19.*|http://172.20.*|http://172.21.*|http://172.22.*|http://172.23.*|http://172.24.*|http://172.25.*|http://172.26.*|http://172.27.*|http://172.28.*|http://172.29.*|http://172.30.*|http://172.31.*|http://192.168.*|http://*.local:*|https://localhost:*|https://127.*|https://10.*|https://172.16.*|https://172.17.*|https://172.18.*|https://172.19.*|https://172.20.*|https://172.21.*|https://172.22.*|https://172.23.*|https://172.24.*|https://172.25.*|https://172.26.*|https://172.27.*|https://172.28.*|https://172.29.*|https://172.30.*|https://172.31.*|https://192.168.*|https://*.local:*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

echo "Signbridge offline proof preflight"
echo ""

if [ "${OFFLINE_MODE:-false}" != "true" ]; then
  fail "OFFLINE_MODE must be true for the offline proof."
fi

if [ "${ALLOW_NETWORK_EGRESS:-true}" != "false" ]; then
  fail "ALLOW_NETWORK_EGRESS must be false for the offline proof."
fi

if [ "${RUNTIME_GPU_REQUIRED:-true}" = "true" ]; then
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    fail "nvidia-smi is missing. Confirm hardware and NVIDIA setup before runtime debugging."
  elif ! nvidia-smi >/dev/null 2>&1; then
    fail "nvidia-smi is installed but cannot see the GPU. Check official device setup before permissions/runtime debugging."
  else
    echo "GPU visibility: ok"
  fi
fi

if [ -z "${LLM_PROVIDER:-}" ] || [ "${LLM_PROVIDER:-mock}" = "mock" ]; then
  warn "LLM_PROVIDER is mock or unset. This can prove UI plumbing, not local model inference."
fi

if [ -n "${LLM_BASE_URL:-}" ] && ! is_localish_url "$LLM_BASE_URL"; then
  fail "LLM_BASE_URL is not localhost, .local, or RFC1918 LAN: $LLM_BASE_URL"
fi

case "${ASR_PROVIDER:-mock}" in
  elevenlabs_api)
    fail "ASR_PROVIDER=elevenlabs_api uses public cloud and is not valid for offline proof."
    ;;
  elevenlabs_on_device)
    if [ "${ELEVENLABS_ON_DEVICE_AVAILABLE:-false}" != "true" ]; then
      fail "ASR_PROVIDER=elevenlabs_on_device selected before official on-device activation is marked available."
    fi
    if [ -z "${ELEVENLABS_PRIVATE_BASE_URL:-}" ] || ! is_localish_url "$ELEVENLABS_PRIVATE_BASE_URL"; then
      fail "ElevenLabs on-device ASR needs a local/private ELEVENLABS_PRIVATE_BASE_URL."
    fi
    ;;
  whisper_cpp|faster_whisper|typed|canned|mock)
    echo "ASR offline path: ${ASR_PROVIDER:-mock}"
    ;;
  *)
    warn "Unknown ASR_PROVIDER=${ASR_PROVIDER:-unset}; verify it is local before demo."
    ;;
esac

case "${TTS_PROVIDER:-mock}" in
  elevenlabs_api)
    fail "TTS_PROVIDER=elevenlabs_api uses public cloud and is not valid for offline proof."
    ;;
  elevenlabs_on_device)
    if [ "${ELEVENLABS_ON_DEVICE_AVAILABLE:-false}" != "true" ]; then
      fail "TTS_PROVIDER=elevenlabs_on_device selected before official on-device activation is marked available."
    fi
    if [ -z "${ELEVENLABS_PRIVATE_BASE_URL:-}" ] || ! is_localish_url "$ELEVENLABS_PRIVATE_BASE_URL"; then
      fail "ElevenLabs on-device TTS needs a local/private ELEVENLABS_PRIVATE_BASE_URL."
    fi
    ;;
  piper|kokoro|espeak_ng|canned|mock)
    echo "TTS offline path: ${TTS_PROVIDER:-mock}"
    ;;
  *)
    warn "Unknown TTS_PROVIDER=${TTS_PROVIDER:-unset}; verify it is local before demo."
    ;;
esac

if [ -n "${ELEVENLABS_PRIVATE_BASE_URL:-}" ] && ! is_localish_url "$ELEVENLABS_PRIVATE_BASE_URL"; then
  fail "ELEVENLABS_PRIVATE_BASE_URL is not local/private: $ELEVENLABS_PRIVATE_BASE_URL"
fi

if [ "${SKIP_RUNTIME_PROBES:-false}" != "true" ] && command -v curl >/dev/null 2>&1 && [ -n "${LLM_BASE_URL:-}" ]; then
  echo ""
  echo "Probing configured LLM models endpoint..."
  if ! curl -fsS --max-time 5 "${LLM_BASE_URL%/}/models" >/dev/null; then
    fail "Configured LLM models endpoint did not respond: ${LLM_BASE_URL%/}/models"
  fi
fi

echo ""
echo "Warnings: $warnings"
echo "Blockers: $failures"

if [ "$failures" -ne 0 ]; then
  exit 1
fi

echo "Offline preflight passed. This does not disable the internet; it verifies the selected runtime path is offline-eligible."
