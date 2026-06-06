# Runtime Environment Variables

Copy `.env.example` to `.env` for local development. Never commit `.env` or real secrets.

Load env for shell probes:

```bash
set -a
source .env
set +a
```

## Core

| Variable | Example | Meaning |
|---|---|---|
| `SIGNBRIDGE_ENV` | `development` | Local environment label. |
| `SIGNBRIDGE_SCENARIO` | `housing_repair` | Demo scenario. Keep aligned with implementation plan. |
| `RUNTIME_TARGET` | `dgx_spark` | Runtime host class: `dgx_spark`, `zgx_nano`, `laptop_dev`, or `unknown`. |
| `RUNTIME_HOSTNAME` | `spark-demo.local` | mDNS/LAN hostname for the runtime device. |
| `RUNTIME_LAN_IP` | `192.168.1.50` | LAN IP used by client devices. |
| `RUNTIME_GPU_REQUIRED` | `true` | Offline proof should require NVIDIA GPU visibility on hardware target. |

## Web And Orchestrator

| Variable | Example | Meaning |
|---|---|---|
| `WEB_PORT` | `3000` | Web client port. |
| `ORCHESTRATOR_HOST` | `0.0.0.0` | Bind host for LAN access during demo. |
| `ORCHESTRATOR_PORT` | `8000` | Orchestrator API/WebSocket port. |
| `ORCHESTRATOR_WS_PATH` | `/ws` | WebSocket path. Do not change event contracts here. |

## LLM Runtime

| Variable | Example | Meaning |
|---|---|---|
| `LLM_PROVIDER` | `llama_cpp` | `nim`, `ollama`, `llama_cpp`, `local_openai`, or `mock`. |
| `LLM_BASE_URL` | `http://spark-demo.local:30000/v1` | OpenAI-compatible local/LAN endpoint. |
| `LLM_MODEL` | `nemotron` | Model ID served by the selected runtime. |
| `LLM_TEST_PROMPT` | optional | Override prompt used by `probe_llm_runtime.sh`. |

## NVIDIA NIM

| Variable | Example | Meaning |
|---|---|---|
| `NGC_API_KEY` | secret | NGC API key. Required for NIM image/model access. |
| `NIM_BASE_URL` | `http://spark-demo.local:8000/v1` | NIM OpenAI-compatible endpoint. |
| `NIM_MODEL` | `meta/llama3-8b-instruct` | NIM model ID. |
| `LOCAL_NIM_CACHE` | `/home/demo/.cache/nim` | Cache path for NIM model assets. |

## Ollama

| Variable | Example | Meaning |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://spark-demo.local:11434` | Native Ollama API base URL. |
| `OLLAMA_HOST` | `0.0.0.0:11434` | Ollama bind setting when serving over LAN. |
| `OLLAMA_MODEL` | `qwen3.6:35b-a3b-nvfp4` | Ollama model tag. |

## llama.cpp

| Variable | Example | Meaning |
|---|---|---|
| `LLAMA_CPP_BASE_URL` | `http://spark-demo.local:30000/v1` | llama.cpp OpenAI-compatible endpoint. |
| `LLAMA_CPP_MODEL_PATH` | `/home/demo/models/nemotron/model.gguf` | Local GGUF path. |
| `LLAMA_CPP_PORT` | `30000` | Server port. |
| `LLAMA_CPP_CTX_SIZE` | `8192` | Context size for demo server. |
| `LLAMA_CPP_GPU_LAYERS` | `99` | GPU offload layer count for demo server. |

## Voice

| Variable | Example | Meaning |
|---|---|---|
| `ASR_PROVIDER` | `whisper_cpp` | `elevenlabs_on_device`, `elevenlabs_api`, `whisper_cpp`, `faster_whisper`, `typed`, `canned`, or `mock`. |
| `TTS_PROVIDER` | `piper` | `elevenlabs_on_device`, `elevenlabs_api`, `piper`, `kokoro`, `espeak_ng`, `canned`, or `mock`. |
| `VOICE_PROBE_ALLOW_NETWORK` | `false` | Set true only when intentionally probing public ElevenLabs API online. |

## ElevenLabs

| Variable | Example | Meaning |
|---|---|---|
| `ELEVENLABS_API_KEY` | secret | Public API key. Not proof of on-device/private access. |
| `ELEVENLABS_ON_DEVICE_AVAILABLE` | `false` | Set true only after official activation and local/private probe. |
| `ELEVENLABS_PRIVATE_BASE_URL` | `http://spark-demo.local:9000` | Private/on-device endpoint if activated. |
| `ELEVENLABS_TTS_MODEL` | `eleven_flash_v2_5` | TTS model ID for API/private mode. |
| `ELEVENLABS_ASR_MODEL` | `scribe_v2_realtime` | ASR model ID for API/private mode. |

## Local Voice Fallbacks

| Variable | Example | Meaning |
|---|---|---|
| `PIPER_VOICE_MODEL` | `/home/demo/models/piper/en_GB.onnx` | Cached Piper voice model. |
| `KOKORO_MODEL_PATH` | `/home/demo/models/kokoro` | Cached Kokoro assets. |
| `WHISPER_CPP_MODEL` | `/home/demo/models/whisper/ggml-small.en.bin` | Cached whisper.cpp model. |
| `FASTER_WHISPER_MODEL` | `/home/demo/models/faster-whisper/small.en` | Cached faster-whisper model. |
| `CANNED_VOICE_DIR` | `demo/voice_samples` | Approved fallback audio. |

## Offline Proof

| Variable | Example | Meaning |
|---|---|---|
| `OFFLINE_MODE` | `true` | Enables offline proof expectations. |
| `ALLOW_NETWORK_EGRESS` | `false` | Must be false for offline proof. |
| `SKIP_RUNTIME_PROBES` | `false` | Set true only when proving config without live services. |

Offline proof forbids `ASR_PROVIDER=elevenlabs_api` and `TTS_PROVIDER=elevenlabs_api`. If ElevenLabs is not privately/on-device activated, use the fallback decision tree.
