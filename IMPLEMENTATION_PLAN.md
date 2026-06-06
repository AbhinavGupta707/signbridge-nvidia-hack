# Signbridge Implementation Plan

Execution plan for the NVIDIA Hack for Impact London build, based on `signbridge-product-spec.md` and the event requirement: autonomous/agentic applications, open models, DGX Spark or ZGX Nano local deployment, positive impact, and City of London open data as a foundation.

Current planning assumption: this is a hackathon build, not a production BSL translator. The winning build is a constrained, honest, polished real-time public-service interpreter demo with a strong local-first privacy proof and an advocacy/record layer grounded in London public data.

## 1. Product Target

Build Signbridge as a desk-side interpreter for a Deaf BSL user attending a London public-service appointment when no human interpreter is available.

The demo must show:

1. A signer uses a constrained BSL vocabulary in a GP, housing, or council-services appointment scenario.
2. The system recognises the signed intent from camera landmarks and speaks fluent English aloud.
3. The hearing professional speaks back and the Deaf user sees live captions.
4. A Policy Agent surfaces a relevant entitlement or service rule with citation.
5. A Question Agent suggests a useful follow-up question.
6. A Record Agent exports a timestamped, citation-backed appointment record.
7. The team pulls the internet connection or disables external egress and the core flow keeps working.

The build must not claim general BSL translation. It should visibly label the scope as "constrained public-service vocabulary" and "not a certified interpreter."

## 2. Recommended Demo Scenario

Choose one scenario and do not expand until the end-to-end path works.

Primary recommendation: housing repair / damp and mould appointment.

Why:

- It sits naturally in Public Services.
- It can use local authority policy and service data more directly than a GP scenario.
- The vocabulary is concrete and demonstrable: home, repair, damp, mould, child, asthma, urgent, appointment, interpreter, complaint, evidence, next step.
- The Policy Agent can surface repair obligations, reasonable adjustments, complaint routes, and documentation requirements.

Fallback scenario: council appointment about accessible communication / requesting BSL support.

Avoid for the first demo: broad clinical diagnosis. Medical scenarios increase safety risk and force the team to caveat too much.

## 3. MVP Scope

### Must Have

- Web client with camera, mic, captions, recognised meaning, confirmation controls, policy cards, question prompts, record export.
- Client-side or server-side MediaPipe landmark extraction.
- A constrained sign/phrase recogniser over recorded demo data.
- Gloss/intent-to-English LLM prompt using a local open model.
- TTS output using ElevenLabs if activated, otherwise local fallback.
- Live ASR captions using ElevenLabs Scribe v2 Realtime if activated, otherwise local fallback or typed/canned fallback for the reverse path.
- Local RAG over a small City of London/London public-service corpus.
- Structured record export as HTML or PDF.
- Offline proof mode with no inference-time internet dependency.

### Should Have

- Confidence threshold and "Is this what you meant?" correction loop.
- Agent activity strip showing `landmarks -> recogniser -> fluency -> speech -> policy -> record`.
- Pre-recorded signing fallback clips that exercise the real recogniser, not a pure video playback.
- End-to-end latency instrumentation displayed privately or in a debug panel.

### Do Not Build Unless Everything Else Works

- General continuous BSL translation.
- English-to-BSL signing avatar.
- Multi-borough policy coverage.
- Multi-signer unconstrained recognition.
- Complex case management integrations.

## 4. Day-Zero Decisions

Make these decisions in the first 45 minutes of execution.

1. Lock the scenario: housing repair is the default.
2. Lock the vocabulary: 20-35 signs/phrases maximum for the live path.
3. Lock the data source set: one City of London/public-service corpus plus one demographic/impact dataset.
4. Lock the model runtime: first working local model server wins.
5. Lock the voice path: ElevenLabs if official activation works; local fallback otherwise.
6. Lock the demo fallback: pre-recorded clips plus deterministic scripted events if live recognition falls below threshold.

Use the project instruction on diagnosis order: if a capability is missing or unavailable, first check registration, discovery, install state, and official activation flow. Only debug permissions/runtime after the feature is actually present.

## 5. Architecture

Use a small monorepo with hard boundaries so agents can work in parallel.

```text
apps/
  web/                         # Next.js or Vite React client
services/
  orchestrator/                # FastAPI + WebSocket event bus
  vision/                      # capture, landmarks, classifier, evaluation
  voice/                       # ASR/TTS providers and fallbacks
  advocacy/                    # ingestion, retrieval, policy/question/record agents
packages/
  contracts/                   # shared event schemas and TypeScript/Python JSON examples
data/
  raw/                         # downloaded public data and policy docs
  sign_clips/                  # local recorded signing clips, if consent allows
  landmarks/                   # extracted landmark arrays
  indexes/                     # local vector index
demo/
  scripts/                     # demo script, runbook, fallback checklist
  clips/                       # approved fallback clips
```

If the existing repo uses a different structure, keep the same ownership boundaries even if paths change.

## 6. Event Contracts

The first implementation task is to create shared JSON contracts. All agents build to these contracts and can mock the other side.

Client to server:

```json
{"type":"session.start","session_id":"demo-001","scenario":"housing_repair","consent_record":true}
{"type":"landmark.frame","session_id":"demo-001","t_ms":1234,"landmarks_version":"mediapipe_holistic_v1","points":[]}
{"type":"audio.chunk","session_id":"demo-001","t_ms":1234,"format":"pcm16","sample_rate":16000,"data_b64":"..."}
{"type":"user.confirmation","utterance_id":"u-7","accepted":true,"correction_text":null}
{"type":"record.export","session_id":"demo-001","format":"html"}
```

Server to client:

```json
{"type":"system.status","component":"voice","status":"ready","detail":"elevenlabs_scribe_v2_realtime"}
{"type":"recognition.partial","utterance_id":"u-7","tokens":["REPAIR","DAMP"],"confidence":0.76}
{"type":"recognition.final","utterance_id":"u-7","tokens":["MY_HOME","DAMP","CHILD_ASTHMA"],"confidence":0.84}
{"type":"translation.final","utterance_id":"u-7","text":"There is damp in my home and it is affecting my child's asthma.","confidence":0.84}
{"type":"tts.audio","utterance_id":"u-7","format":"wav","data_b64":"..."}
{"type":"caption.partial","speaker":"professional","text":"I can book an inspection for..."}
{"type":"policy.card","id":"p-2","title":"Reasonable adjustments","claim":"The service should provide accessible communication support on request.","source_title":"...","source_url":"...","quote":"..."}
{"type":"question.prompt","id":"q-3","text":"Ask when the repair inspection will happen and how it will be confirmed in writing."}
{"type":"record.updated","session_id":"demo-001","item_count":8}
```

Do not let feature teams invent new event shapes during the hackathon. Additive changes only, reviewed by the integration lead.

## 7. Workstreams and Parallel Agent Plan

### Agent 0: Integration Lead

Owns:

- Repo scaffold.
- Shared contracts.
- Local dev commands.
- WebSocket orchestrator shell.
- Mock providers for every downstream component.
- Merge sequencing and end-to-end smoke tests.

Files:

- `packages/contracts/**`
- `services/orchestrator/**`
- root config and scripts

Deliverables:

- `make dev` or equivalent starts orchestrator plus web mocks.
- `/health` returns component status.
- `/ws` can replay a scripted demo from JSON events.
- All other agents can run against mocks before their real component is ready.

Acceptance:

- A frontend can connect and receive mock `recognition`, `translation`, `caption`, `policy`, `question`, and `record` events.

### Agent A: Hardware, Activation, and Runtime

Owns:

- DGX Spark/ZGX Nano access.
- Official activation/discovery flows.
- Model serving runtime.
- Offline proof environment.

Files:

- `infra/**`
- `.env.example`
- `demo/OFFLINE_PROOF.md`
- deployment scripts

Tasks:

1. Confirm hardware model, OS, architecture, GPU visibility, RAM, storage.
2. Confirm network plan: dedicated LAN, client device can reach server.
3. Confirm CUDA/NVIDIA container stack.
4. Check NVIDIA NIM/Ollama/llama.cpp availability using official install/discovery flows.
5. Check ElevenLabs sponsor access: account, entitlement, private/on-device docs, containers or API keys.
6. If ElevenLabs on-device is unavailable, mark it unavailable and enable local fallback; do not waste the sprint debugging nonexistent access.
7. Preload local model weights and public data before the offline demo.
8. Produce a one-command startup script.

Acceptance:

- Local model server responds to a prompt.
- TTS provider speaks a short phrase or fallback speaks it.
- ASR provider transcribes a short microphone sample or fallback is selected.
- Internet can be disabled and the chosen offline subset still works.

### Agent B: Vision and Sign Recognition

Owns:

- Camera/clip capture.
- MediaPipe landmarks.
- Training data format.
- Constrained recogniser.
- Confidence and fallback clips.

Files:

- `services/vision/**`
- `data/sign_clips/**`
- `data/landmarks/**`
- `demo/clips/**`

Tasks:

1. Define the 20-35 sign/phrase vocabulary for the chosen scenario.
2. Record 5-10 takes per phrase in demo lighting. If a Deaf collaborator is available, capture their data with explicit consent; otherwise record team-member prototype data and state the limitation.
3. Extract landmarks to `.npz` or `.jsonl`.
4. Build a baseline recogniser first: template matching / dynamic time warping / nearest centroid over normalised landmark sequences.
5. Add a lightweight classifier only if the baseline is insufficient and time allows.
6. Emit `recognition.partial` and `recognition.final` events to the orchestrator.
7. Add a confidence threshold. Low confidence should trigger confirmation or fallback rather than hallucinated speech.

Acceptance:

- Recognises at least 10 scripted phrases at 80%+ top-1 accuracy in demo conditions, or clearly falls back.
- End-to-end from clip/camera to `recognition.final` works under 500 ms after phrase completion for the scripted set.

### Agent C: LLM Fluency and Voice

Owns:

- Gloss/intent-to-English rewriting.
- TTS.
- ASR captions.
- Provider fallback abstraction.

Files:

- `services/voice/**`
- `services/orchestrator/providers/translation*`
- `demo/voice_samples/**`

Tasks:

1. Implement a deterministic template map for the demo vocabulary.
2. Implement a local LLM prompt for more natural phrasing, with the template as a fallback.
3. Keep the LLM prompt short: scenario, token glossary, last 3 utterances, safety instruction not to add facts.
4. Implement TTS provider interface: ElevenLabs first if activated; Piper/Kokoro/espeak-ng fallback if not.
5. Implement ASR provider interface: ElevenLabs Scribe v2 Realtime if activated; whisper.cpp/faster-whisper fallback if usable; typed/canned reverse-flow fallback if necessary.
6. Stream partial captions to the UI where possible.

Acceptance:

- Given `["MY_HOME","DAMP","CHILD_ASTHMA"]`, system produces a natural sentence and speaks it.
- Given microphone speech, system produces captions or the fallback is explicitly selected.
- No cloud dependency exists in the offline proof mode unless the team decides to show a separate sponsor-quality mode before the offline proof.

### Agent D: Advocacy and Open Data

Owns:

- City of London/London open data foundation.
- Policy corpus.
- Retrieval.
- Policy Agent, Question Agent, Record Agent.

Files:

- `services/advocacy/**`
- `data/raw/**`
- `data/indexes/**`
- `demo/sources.md`

Tasks:

1. Select one domain corpus tied to the scenario. For housing, use City of London Corporation service/policy pages, public housing/repairs guidance, complaints/accessibility pages, and relevant London Datastore/ONS demographic context.
2. Download or save local copies before demo.
3. Chunk documents with stable source metadata: `source_title`, `source_url`, `retrieved_at`, `section`, `quote`.
4. Build embeddings with a local model and Qdrant/LanceDB/FAISS.
5. Implement `policy.card` generation with citations. Every claim must trace to a source.
6. Implement `question.prompt` using scenario state and retrieved policy.
7. Implement `record.export` as HTML first; PDF only if easy.
8. Include the City of London open-data connection in the record and pitch.

Acceptance:

- For a damp/repair utterance, a policy card appears with a citation.
- For an appointment/next-step utterance, a useful question prompt appears.
- Exported record includes transcript, accepted/corrected translations, policy cards, commitments, next steps, and source list.

### Agent E: Frontend and Demo UX

Owns:

- User-facing app.
- Camera/mic capture.
- Caption and confirmation UI.
- Agent activity strip.
- Demo mode.

Files:

- `apps/web/**`

Tasks:

1. Build the actual interpreter screen as the first screen; no landing page.
2. Create clear zones:
   - Deaf user captions.
   - Recognised signed meaning with confirmation.
   - Spoken output status.
   - Policy/question cards for the professional.
   - Record/export controls.
   - Agent activity strip.
3. Connect to mock WebSocket first.
4. Add camera/mic permissions and clear state for disconnected/offline/missing provider.
5. Keep text large, calm, and readable at demo distance.
6. Add a visible but unobtrusive limitation label: constrained demo, not certified interpretation.
7. Add demo controls hidden behind a small operator panel: replay clip, reset session, force fallback, export record.

Acceptance:

- The app runs from a laptop/tablet on the local LAN.
- A judge can understand the pipeline state without reading logs.
- Text does not overflow or overlap at laptop and tablet sizes.

### Agent F: Demo, Safety, and Pitch

Owns:

- Script.
- Evidence cards.
- Rehearsal.
- Ethical framing.
- Fallback decision tree.

Files:

- `demo/RUNBOOK.md`
- `demo/PITCH.md`
- `demo/FALLBACKS.md`
- `demo/REHEARSAL_CHECKLIST.md`

Tasks:

1. Write a 3-minute script with exact lines and exact signs/phrases.
2. Prepare one slide or UI card with impact evidence: BSL users, interpreter gap, local privacy need.
3. Prepare source notes for judges.
4. Prepare fallback ladder:
   - live signing
   - prerecorded signing clips through recogniser
   - scripted recogniser events
   - UI-only walkthrough
5. Rehearse with timer at least 3 times.
6. Own the phrase "augmentation, not replacement."

Acceptance:

- Anyone on the team can run the demo from the runbook.
- Fallback can be activated without explaining a failure awkwardly.
- The team can answer "is this general BSL translation?" honestly and confidently.

## 8. Non-Conflicting Parallelisation Map

These can start immediately in parallel after Agent 0 publishes contracts:

- Agent B vision can emit events into mocks without waiting for voice.
- Agent C voice can consume static `recognition.final` examples without waiting for vision.
- Agent D advocacy can consume static transcript examples without waiting for voice or vision.
- Agent E frontend can run entirely from mocked events until real services connect.
- Agent A infrastructure can work independently as long as it does not change event contracts.
- Agent F demo can draft script and vocabulary while Agent B validates recognisability.

Potential conflicts:

- `packages/contracts/**`: only Agent 0 edits.
- root dependency files: Agent 0 coordinates all changes.
- WebSocket event names: Agent 0 approves additive changes.
- Scenario/vocabulary: Agent F proposes, Agent B validates, Agent 0 freezes.
- Provider selection: Agent A discovers availability, Agent C implements provider interface.

Integration order:

1. Frontend + orchestrator mock replay.
2. Vision real events into orchestrator.
3. Translation + TTS from real recognition events.
4. ASR captions into frontend.
5. Advocacy from transcript events.
6. Record export.
7. Offline proof.

### GitHub Branch Protocol

Use GitHub as the coordination surface for parallel Codex sessions.

- `main` is integration only.
- Start each parallel session from one branch:
  - `agent/integration-scaffold`
  - `agent/runtime-activation`
  - `agent/vision-recognition`
  - `agent/voice-llm`
  - `agent/advocacy-data`
  - `agent/frontend-demo-ux`
  - `agent/demo-safety-pitch`
- Each branch owns the paths listed in `docs/BRANCHING_AND_PARALLEL_AGENTS.md`.
- Shared event contracts in `packages/contracts/**` are owned by the integration lead.
- Feature branches must run against mocks before expecting other branches to merge.
- Open PRs back to `main`; include validation, provider assumptions, and intentionally touched files.
- If a feature is missing or unavailable, follow the project diagnosis order: check registration, discovery, install state, and official activation first, then runtime and permissions.

Initial scaffolding is required before broad parallel execution. The scaffold should publish contracts, mocks, branch ownership, and repo layout. Once that is merged, the six feature workstreams can proceed concurrently.

## 9. Critical Path Timeline

Assuming execution starts on Saturday 6 June 2026.

### Hour 0-1: Scope and Contracts

- Freeze scenario and vocabulary.
- Create repo structure and event schemas.
- Start mock orchestrator and mock frontend.
- Begin hardware/activation discovery.

Exit gate:

- Mock demo can run in UI.
- Hardware and sponsor access status is known or actively being activated.

### Hour 1-3: Real Inputs

- Record first training clips.
- Extract landmarks.
- Implement baseline recogniser.
- Select local LLM and TTS/ASR provider path.
- Start public data ingestion.

Exit gate:

- One signed phrase becomes one `recognition.final`.
- One English sentence is spoken locally or by selected provider.
- One source document is retrievable.

### Hour 3-6: First End-to-End

- Wire vision -> translation -> TTS.
- Wire ASR/captions or fallback.
- Wire first policy card.
- UI shows activity strip and confirmation loop.

Exit gate:

- One complete appointment exchange works with mocks or partial real components.

### Hour 6-10: Robust Demo Path

- Expand to 10-15 phrases.
- Add confidence thresholds.
- Add record export.
- Add offline mode switch/runbook.
- Rehearse fallback.

Exit gate:

- The 3-minute demo works twice in a row.

### Sunday Morning: Polish and Proof

- Improve UI readability.
- Lock camera/lighting/network setup.
- Freeze code except emergency fixes.
- Rehearse live and fallback modes.
- Prepare answer sheet for judges.

Exit gate:

- Live path or prerecorded-through-recogniser path works reliably.
- Offline proof works.
- Record export works.

## 10. Technical Implementation Details

### Vision

Prioritise robustness over model sophistication.

Input:

- Webcam frames or prerecorded clips.
- MediaPipe Holistic landmarks.

Preprocessing:

- Normalise by torso/shoulder width.
- Use hands plus selected pose landmarks.
- Smooth landmark jitter with a small rolling average.
- Segment phrases by operator trigger first; automatic silence/hold detection only if time allows.

Recognition options in order:

1. Phrase-level nearest-template recogniser.
2. Dynamic time warping over landmark sequences.
3. Lightweight temporal CNN/BiLSTM classifier.

Do not start with a Transformer unless the simpler path already works.

### Translation

Use two layers:

1. Deterministic phrase templates for demo safety.
2. Local LLM rewrite for fluent natural English.

Prompt constraints:

- Only translate the provided tokens.
- Do not invent symptoms, commitments, dates, names, legal advice, or medical claims.
- Preserve uncertainty if confidence is low.
- Return one sentence suitable for TTS.

### Voice

Provider order:

1. ElevenLabs Scribe v2 Realtime and TTS if officially activated and usable.
2. Local ASR/TTS fallback.
3. Canned/typed reverse path only as a labelled fallback.

Important: public ElevenLabs docs show Scribe v2 Realtime via API and private/on-device deployment as enterprise/early-access. Treat on-device as an activation dependency, not a guaranteed default.

### Advocacy

Implement simple RAG; avoid agent framework complexity until retrieval works.

Policy Agent:

- Trigger from translated utterances and professional captions.
- Retrieve 3-5 chunks.
- Emit one concise policy card with citation.

Question Agent:

- Generate one practical question at a time.
- Prefer procedural questions: timescale, written confirmation, escalation route, accessible communication, evidence needed.

Record Agent:

- Append every accepted utterance.
- Include corrections.
- Include policy cards and source URLs.
- Include commitments and next steps.
- Export HTML with a print stylesheet.

## 11. Data Plan

Use public data to satisfy the event requirement in two ways:

1. Impact targeting: London/ONS/London Datastore disability, health, deprivation, or service-access datasets.
2. Operational value: City of London Corporation service/policy pages and open datasets relevant to the selected public-service scenario.

Minimum local corpus:

- One page/document on housing repairs or relevant service process.
- One page/document on complaints or escalation.
- One page/document on accessibility/reasonable adjustments.
- One demographic/impact source for London or City of London.

Data requirements:

- Save local copies before the demo.
- Store `source_url` and `retrieved_at`.
- Do not cite unverified figures in the UI.
- If a hearing-specific borough dataset cannot be found quickly, use disability/accessibility data and state the limitation.

## 12. Reliability Strategy

This project wins if the demo feels real and honest. It loses if the team overclaims or the live pipeline collapses.

Reliability rules:

- Every component needs a mock.
- Every external provider needs a fallback.
- Every recognition result needs confidence.
- Every policy claim needs a source.
- Every demo path needs a rehearsed fallback.
- Freeze features once the demo works twice.

Fallback ladder:

1. Live camera recognition.
2. Prerecorded signing clips fed through the real landmark/recogniser pipeline.
3. Precomputed landmark files fed through recogniser.
4. Scripted event replay through orchestrator.

The fallback should still demonstrate architecture and privacy. Do not make the fallback feel like a separate fake product.

## 13. Acceptance Criteria

The hackathon MVP is complete when:

- The client connects to the local server over LAN.
- The UI shows consent/session state.
- At least 10 scripted signed phrases produce spoken English.
- Professional speech produces live captions, or fallback is explicitly selected.
- At least one relevant policy card appears with a citation.
- At least one question prompt appears.
- Record export produces a readable HTML/PDF artifact.
- Offline proof works for the selected demo path.
- Demo script completes in under 3 minutes 30 seconds.
- The team can state limitations clearly: constrained vocabulary, not certified, co-design required for production.

## 14. Judge Narrative

Lead with:

"This is for the moment a Deaf BSL user is in a public-service appointment and no interpreter is available. Signbridge runs the sensitive video, language, speech, and policy agents locally on the DGX Spark, so no raw conversation leaves the room."

Then show:

- Sign -> spoken English.
- Speech -> captions.
- Policy card.
- Question prompt.
- Offline proof.
- Exported record.

Close with:

"We are not replacing interpreters. We are covering the unplanned gap, with consent, citations, and a record the user controls. Production requires Deaf-led co-design and larger licensed BSL training data."

## 15. Research Notes Checked During Planning

- GOV.UK BSL Report 2022 states around 151,000 BSL users in the UK, 87,000 of whom are Deaf, and cites RNID's 1 in 5 / 12 million Deaf or hard-of-hearing figure.
- NVIDIA's DGX Spark materials describe GB10 Grace Blackwell, 128 GB unified memory, and local AI agent/model workflows.
- NVIDIA's DGX Spark developer materials list local model-serving paths such as llama.cpp / TensorRT-LLM and current open model examples.
- ElevenLabs public docs describe Scribe v2 Realtime and private/on-device deployment options, but private/on-device access requires enterprise or authorized access.
- London Datastore is an official open-data portal for London datasets; City of London Corporation pages and government data sources should be used for the scenario-specific corpus.

Primary links:

- GOV.UK BSL Report 2022: https://www.gov.uk/government/publications/the-british-sign-language-bsl-report-2022/the-british-sign-language-bsl-report-2022
- NVIDIA DGX Spark: https://www.nvidia.com/en-us/products/workstations/dgx-spark/
- NVIDIA DGX Spark llama.cpp guide: https://build.nvidia.com/spark/llama-cpp
- ElevenLabs models docs: https://elevenlabs.io/docs/models
- ElevenLabs private deployment docs: https://elevenlabs.io/docs/developers/private-deployment/overview
- ElevenLabs local deployment blog: https://elevenlabs.io/blog/enterprise-voice-ai-deployed-locally
- London Datastore: https://data.london.gov.uk/
- City of London data and statistics: https://www.cityoflondon.gov.uk/services/planning/planning-policy/data-and-statistics
