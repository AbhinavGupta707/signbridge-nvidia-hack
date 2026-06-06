#!/usr/bin/env bash
set -u

BASE_URL="${1:-${LLM_BASE_URL:-http://127.0.0.1:30000/v1}}"
MODEL="${2:-${LLM_MODEL:-nemotron}}"
PROMPT="${LLM_TEST_PROMPT:-Rewrite this as a short public-service appointment sentence: MY_HOME DAMP CHILD_ASTHMA}"

if ! command -v curl >/dev/null 2>&1; then
  echo "BLOCKED: curl is required for the LLM probe." >&2
  exit 2
fi

echo "Probing OpenAI-compatible LLM runtime"
echo "Base URL: $BASE_URL"
echo "Model: $MODEL"
echo ""

echo "Checking models endpoint..."
if ! curl -fsS --max-time 10 "$BASE_URL/models"; then
  echo ""
  echo "BLOCKED: models endpoint is not reachable. Check runtime registration/discovery/install before debugging permissions." >&2
  exit 1
fi

echo ""
echo ""
echo "Checking chat completions endpoint..."
CHAT_PAYLOAD=$(printf '{"model":"%s","messages":[{"role":"system","content":"Return one concise sentence. Do not add facts."},{"role":"user","content":"%s"}],"max_tokens":48,"temperature":0}' "$MODEL" "$PROMPT")

if curl -fsS --max-time 30 \
  -H "Content-Type: application/json" \
  -d "$CHAT_PAYLOAD" \
  "$BASE_URL/chat/completions"; then
  echo ""
  echo "LLM runtime probe passed via /chat/completions."
  exit 0
fi

echo ""
echo "Chat completions failed; trying legacy completions endpoint..."
COMPLETIONS_PAYLOAD=$(printf '{"model":"%s","prompt":"%s","max_tokens":48,"temperature":0}' "$MODEL" "$PROMPT")

if curl -fsS --max-time 30 \
  -H "Content-Type: application/json" \
  -d "$COMPLETIONS_PAYLOAD" \
  "$BASE_URL/completions"; then
  echo ""
  echo "LLM runtime probe passed via /completions."
  exit 0
fi

echo ""
echo "BLOCKED: LLM runtime is discoverable but no completion endpoint responded." >&2
echo "Follow the runtime's official activation and serving flow before changing app code." >&2
exit 1
