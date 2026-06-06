# Open Flags

These are not blockers for scaffolding. They are the questions to answer before deep implementation or before a judge-facing claim.

## Terminology

- The product spec and event details refer to DGX Spark and ZGX Nano. If anyone says "Codex Spark", confirm whether they mean NVIDIA DGX Spark.

## Sponsor Access

- ElevenLabs on-device access is not guaranteed by public docs. It needs official event/sponsor activation.
- If unavailable, the demo should use local fallback ASR/TTS for the offline proof and can optionally show API-backed ElevenLabs in a separate sponsor-quality mode.
- A public ElevenLabs API key should be labelled `api_only`, not on-device/private activation.

## Runtime Activation

- NIM requires NGC account/key, NIM entitlement, Docker, and NVIDIA Container Toolkit before runtime debugging is useful.
- Ollama requires official install/discovery and a downloaded local model before GPU troubleshooting is useful.
- llama.cpp requires source checkout/build artifacts and a local GGUF before CUDA/runtime tuning is useful.
- Any offline proof path that still needs public internet is blocked until a local/on-device fallback is selected.

## Data Specificity

- The City of London housing/damp-mould scenario is currently the strongest data fit.
- If the team wants a GP scenario, it needs a credible local policy corpus and more careful medical safety language.
- Hearing-specific borough-level data may not be available quickly. Use disability/accessibility datasets if needed and be explicit about the limitation.

## BSL Recognition Scope

- Weekend build should use constrained phrases and explicit confidence thresholds.
- Production path requires Deaf-led co-design and licensed large-scale BSL data.
- Do not claim certified interpretation or general continuous BSL translation.

## Privacy and Governance

- Raw video should not be retained.
- Records should be consent-gated.
- A production deployment requires DPIA, retention policy, audit model, and public-body governance.
