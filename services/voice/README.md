# Voice and LLM

Gloss-to-English translation, TTS, and ASR providers live here. This service uses the shared event contract in `packages/contracts` and does not define new event shapes.

## Architecture

- `signbridge_voice.translation`: gloss/token to English providers.
- `signbridge_voice.prompts`: local LLM prompt design with strict no-invention rules.
- `signbridge_voice.tts`: TTS provider interface, ElevenLabs adapter, local/canned/mock fallbacks.
- `signbridge_voice.asr`: ASR provider interface, Scribe v2 Realtime boundary, local/typed/mock fallbacks.
- `signbridge_voice.providers`: orchestrator-compatible bundle with `translation`, `tts`, and `captions` attributes.

## Provider Selection

Provider order follows activation state, not wishful configuration:

1. ElevenLabs private/on-device only when `ELEVENLABS_ON_DEVICE_AVAILABLE=true` and `ELEVENLABS_PRIVATE_BASE_URL` is set.
2. Public ElevenLabs API only when explicitly selected, `ALLOW_NETWORK_EGRESS=true`, and `OFFLINE_MODE=false`.
3. Local fallback (`piper`, `espeak-ng`, `whisper-cli`, typed/canned captions) for offline proof.
4. Mock providers for integration wiring only.

An ElevenLabs API key alone is `api_only`, not on-device activation.

## Gloss To English

`TemplateGlossTranslator` is the demo-safety default. It maps known constrained gloss sequences to fixed English sentences and uses confirmation-style text for unknown or low-confidence tokens.

`LocalLLMGlossTranslator` calls a local OpenAI-compatible `/chat/completions` endpoint only when `LLM_PROVIDER` is not `mock` and `LLM_BASE_URL` is localhost/LAN/private, unless network egress is explicitly allowed. Exact demo templates still win before the LLM. The prompt requires strict JSON and forbids adding policy advice, clinical claims, dates, names, legal rights, sources, or promises. If the model output is invalid or contains unsupported fact patterns, the template fallback is used.

## TTS

Set `TTS_PROVIDER` to:

- `elevenlabs_on_device` or `elevenlabs_private`: uses ElevenLabs only after private/on-device activation gates pass.
- `elevenlabs_api`: online sponsor-quality mode only; never offline proof.
- `piper`, `espeak_ng`, `local`, `auto`, or `canned`: local fallback modes.
- `mock`: contract-valid placeholder WAV, not a spoken TTS proof.

Optional variables:

- `ELEVENLABS_VOICE_ID`
- `PIPER_VOICE_MODEL`
- `CANNED_VOICE_DIR`

## ASR

Set `ASR_PROVIDER` to:

- `elevenlabs_on_device` or `elevenlabs_private`: selects the Scribe v2 Realtime boundary only after private/on-device activation gates pass.
- `elevenlabs_api`: online sponsor-quality mode only.
- `whisper_cpp`, `local`, or `auto`: local `whisper-cli` if installed and `WHISPER_CPP_MODEL` is cached.
- `typed` or `canned`: labelled reverse-path fallback.
- `mock`: scripted caption events only.

The Scribe v2 Realtime class is intentionally an activation-gated interface. Runtime work should attach the concrete streaming adapter after the official endpoint shape is discovered.

## Latency Notes

- Template translation target: under 100 ms after `recognition.final`.
- Local LLM rewrite target: under 600 ms for short constrained token lists; fallback if slow or invalid.
- TTS target: under 300 ms for local command or ElevenLabs Flash-class models after warm start.
- ASR partial captions target: under 250 ms when Scribe v2 Realtime or local ASR is ready; typed/canned fallback is labelled and deterministic.
- Offline proof should preload models and audio assets before disabling egress.

## Offline Mode

For offline proof, use:

```bash
OFFLINE_MODE=true
ALLOW_NETWORK_EGRESS=false
TTS_PROVIDER=local
ASR_PROVIDER=typed
LLM_PROVIDER=<local_openai_provider>
LLM_BASE_URL=http://<local-or-lan-host>:<port>/v1
```

If local TTS/ASR binaries are unavailable, the provider emits contract-valid mock/canned events but the demo must not claim live local TTS or ASR.

## Smoke Test

From the repo root:

```bash
python3 -m services.voice.tools.voice_smoke --mock
python3 -m services.voice.tools.voice_smoke --mock --json
```
