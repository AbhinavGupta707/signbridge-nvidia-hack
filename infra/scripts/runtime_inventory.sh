#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT_PATH="${1:-${TMPDIR:-/tmp}/signbridge_runtime_discovery_report.md}"

mkdir -p "$(dirname "$REPORT_PATH")"

append() {
  printf "%s\n" "$*" >> "$REPORT_PATH"
}

section() {
  append ""
  append "## $1"
}

run_capture() {
  local label="$1"
  shift
  append ""
  append "### $label"
  append ""
  append '```text'
  if "$@" >> "$REPORT_PATH" 2>&1; then
    true
  else
    local code=$?
    append "[command exited with status $code]"
  fi
  append '```'
}

command_status() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    printf "present at %s" "$(command -v "$name")"
  else
    printf "missing"
  fi
}

env_status() {
  local name="$1"
  local value="${!name-}"
  if [ -n "$value" ]; then
    printf "set"
  else
    printf "unset"
  fi
}

probe_url() {
  local label="$1"
  local url="$2"
  append ""
  append "### $label"
  append ""
  append '```text'
  if command -v curl >/dev/null 2>&1; then
    curl -fsS --max-time 3 "$url" >> "$REPORT_PATH" 2>&1
    local code=$?
    if [ "$code" -ne 0 ]; then
      append "[curl exited with status $code]"
    fi
  else
    append "curl missing"
  fi
  append '```'
}

cd "$ROOT_DIR" || exit 1
: > "$REPORT_PATH"

append "# Signbridge Runtime Discovery Report"
append ""
append "- Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
append "- Working tree: $ROOT_DIR"
append "- Diagnosis order: registration and official activation, discovery, install state, then runtime and permissions."
append "- Scope: read-only discovery. This script does not install software, download models, or change app contracts."

section "Operator Inputs"
append ""
append "| Input | Status | Notes |"
append "|---|---|---|"
append "| RUNTIME_TARGET | ${RUNTIME_TARGET:-unset} | Expected: dgx_spark, zgx_nano, laptop_dev, or unknown. |"
append "| RUNTIME_HOSTNAME | ${RUNTIME_HOSTNAME:-unset} | DGX Spark mDNS name or LAN hostname when known. |"
append "| RUNTIME_LAN_IP | ${RUNTIME_LAN_IP:-unset} | LAN address the web client should use. |"
append "| OFFLINE_MODE | ${OFFLINE_MODE:-unset} | Should be true for the offline proof. |"
append "| ALLOW_NETWORK_EGRESS | ${ALLOW_NETWORK_EGRESS:-unset} | Should be false for the offline proof. |"
append "| LLM_PROVIDER | ${LLM_PROVIDER:-unset} | nim, ollama, llama_cpp, local_openai, or mock. |"
append "| ASR_PROVIDER | ${ASR_PROVIDER:-unset} | elevenlabs_on_device, elevenlabs_api, whisper_cpp, faster_whisper, typed, canned, or mock. |"
append "| TTS_PROVIDER | ${TTS_PROVIDER:-unset} | elevenlabs_on_device, elevenlabs_api, piper, kokoro, espeak_ng, canned, or mock. |"
append "| ELEVENLABS_API_KEY | $(env_status ELEVENLABS_API_KEY) | Redacted. API access is not proof of on-device/private access. |"
append "| ELEVENLABS_PRIVATE_BASE_URL | ${ELEVENLABS_PRIVATE_BASE_URL:-unset} | Required for private/on-device network probes. |"
append "| ELEVENLABS_ON_DEVICE_AVAILABLE | ${ELEVENLABS_ON_DEVICE_AVAILABLE:-unset} | Must be true only after official activation and a local/private probe. |"
append "| NGC_API_KEY | $(env_status NGC_API_KEY) | Redacted. Required for NIM container pulls/model resources. |"

section "Host Identity"
run_capture "hostname" hostname
run_capture "uname" uname -a
if command -v lsb_release >/dev/null 2>&1; then
  run_capture "lsb_release" lsb_release -a
elif command -v sw_vers >/dev/null 2>&1; then
  run_capture "sw_vers" sw_vers
fi
run_capture "architecture" uname -m
run_capture "disk space" df -h /
if command -v free >/dev/null 2>&1; then
  run_capture "memory" free -h
elif command -v vm_stat >/dev/null 2>&1; then
  run_capture "memory" vm_stat
fi

section "NVIDIA And CUDA Discovery"
append ""
append "| Check | Status |"
append "|---|---|"
append "| nvidia-smi | $(command_status nvidia-smi) |"
append "| nvcc | $(command_status nvcc) |"
append "| nvidia-ctk | $(command_status nvidia-ctk) |"
if command -v nvidia-smi >/dev/null 2>&1; then
  run_capture "nvidia-smi summary" nvidia-smi
  run_capture "gpu query" nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
fi
if command -v nvcc >/dev/null 2>&1; then
  run_capture "nvcc version" nvcc --version
fi

section "Container Runtime Discovery"
append ""
append "| Check | Status |"
append "|---|---|"
append "| docker | $(command_status docker) |"
append "| docker compose | $(command_status docker-compose) |"
if command -v docker >/dev/null 2>&1; then
  run_capture "docker version" docker --version
  run_capture "docker runtimes" docker info --format "{{json .Runtimes}}"
fi
if command -v nvidia-ctk >/dev/null 2>&1; then
  run_capture "nvidia-ctk version" nvidia-ctk --version
fi

section "Model Runtime Discovery"
append ""
append "| Runtime | Discovery | Default probe |"
append "|---|---|---|"
append "| NIM | NGC key $(env_status NGC_API_KEY), docker $(command_status docker) | ${NIM_BASE_URL:-http://127.0.0.1:8000/v1}/models |"
append "| Ollama | $(command_status ollama) | ${OLLAMA_BASE_URL:-http://127.0.0.1:11434}/api/tags |"
append "| llama.cpp | llama-server $(command_status llama-server), cmake $(command_status cmake), git $(command_status git) | ${LLAMA_CPP_BASE_URL:-http://127.0.0.1:30000/v1}/models |"
if command -v ollama >/dev/null 2>&1; then
  run_capture "ollama version" ollama --version
  probe_url "ollama tags" "${OLLAMA_BASE_URL:-http://127.0.0.1:11434}/api/tags"
fi
if command -v pgrep >/dev/null 2>&1; then
  run_capture "llama-server processes" pgrep -af llama-server
fi
probe_url "configured LLM models endpoint" "${LLM_BASE_URL:-http://127.0.0.1:30000/v1}/models"
probe_url "NIM models endpoint" "${NIM_BASE_URL:-http://127.0.0.1:8000/v1}/models"
probe_url "llama.cpp models endpoint" "${LLAMA_CPP_BASE_URL:-http://127.0.0.1:30000/v1}/models"

section "Voice Runtime Discovery"
append ""
append "| Runtime | Status | Notes |"
append "|---|---|---|"
append "| ElevenLabs public API key | $(env_status ELEVENLABS_API_KEY) | Cloud API key alone is not on-device activation. |"
append "| ElevenLabs private base URL | ${ELEVENLABS_PRIVATE_BASE_URL:-unset} | Probe only after sponsor/private deployment activation. |"
append "| Piper | $(command_status piper) | Local TTS fallback candidate. |"
append "| Kokoro CLI | $(command_status kokoro) | Local TTS fallback candidate when installed. |"
append "| espeak-ng | $(command_status espeak-ng) | Lowest-risk deterministic local TTS fallback. |"
append "| whisper.cpp CLI | $(command_status whisper-cli) | Local ASR fallback candidate. |"
append "| faster-whisper | $(command_status faster-whisper) | Local ASR fallback candidate. |"
if [ -n "${ELEVENLABS_PRIVATE_BASE_URL:-}" ]; then
  probe_url "ElevenLabs private models endpoint" "${ELEVENLABS_PRIVATE_BASE_URL%/}/v1/models"
fi

section "LAN And Listening Services"
if command -v ip >/dev/null 2>&1; then
  run_capture "ip addr" ip addr
elif command -v ifconfig >/dev/null 2>&1; then
  run_capture "ifconfig" ifconfig
fi
if command -v ss >/dev/null 2>&1; then
  run_capture "listening tcp sockets" ss -tulpen
elif command -v lsof >/dev/null 2>&1; then
  run_capture "listening tcp sockets" lsof -nP -iTCP -sTCP:LISTEN
fi

section "Discovery Gate Notes"
append ""
append "- Missing hardware: confirm the assigned device, mDNS/LAN identity, and official NVIDIA/HP setup flow before investigating drivers."
append "- Missing NIM: confirm NGC account, NGC API key, NIM catalog entitlement, and container image availability before debugging Docker permissions."
append "- Missing Ollama: confirm DGX Spark/Ollama playbook support and installed Ollama version before GPU troubleshooting."
append "- Missing llama.cpp: confirm source checkout/build artifacts/model file path before tuning CUDA flags."
append "- Missing ElevenLabs on-device/private: confirm sponsor account, entitlement, private deployment docs, deployment artifact, and local/private endpoint before debugging voice runtime code."
append "- Offline proof blocker: any required inference path that needs public internet while OFFLINE_MODE=true."

append ""
append "Report written to: $REPORT_PATH"
printf "Runtime discovery report written to %s\n" "$REPORT_PATH"
