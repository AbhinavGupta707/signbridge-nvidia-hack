# Signbridge — Product & Technical Specification

**A real-time British Sign Language ↔ speech interpreter that runs entirely on-device.**

| | |
|---|---|
| **Version** | 0.1 (hackathon build spec) |
| **Event** | NVIDIA Hack for Impact — London, 5–7 June 2026 |
| **Track** | Public Services |
| **Hardware** | NVIDIA DGX Spark / ZGX Nano (GB10 Grace Blackwell, 128 GB unified memory) |
| **Model sponsor fit** | ElevenLabs (multilingual TTS for the spoken output, Scribe v2 ASR for the reverse direction) |
| **Risk profile** | **High ceiling, high risk.** Highest demo "wow"; the vision pipeline is the crux and must be scoped honestly. |
| **One-liner** | A camera watches a Deaf person sign; within about a second the room hears fluent spoken English — and the hearing person's speech comes back as live captions. All of it runs on one box in the room; no video ever leaves it. |

---

## 1. Executive summary

Signbridge gives a Deaf BSL user a way to communicate in a public-service appointment when no human interpreter is available — which, given the interpreter shortage, is most of the time. A camera captures the signer; an on-device vision pipeline recognises the signs; a language model assembles them into fluent English; and ElevenLabs speaks it aloud. In the reverse direction, the hearing person's speech is transcribed live (ElevenLabs Scribe v2) and shown to the Deaf user as captions (with an experimental signing-avatar option).

Behind the interpretation layer, Signbridge reuses the **advocacy stack** from its sibling product Bridge — a **Policy Agent**, a **Question Agent**, and a **Record Agent** — all grounded in London open data, so the system doesn't just translate, it helps the Deaf user get the entitlement they're owed and walk away with an appeal-ready record.

The product is only possible on a local box: continuous video of someone communicating in a clinical or legal setting is among the most sensitive biometric data imaginable and cannot be streamed to a cloud API, and the vision + language + speech models must run concurrently with low latency for natural turn-taking.

**This spec is deliberately honest about scope.** A weekend build delivers a *constrained-vocabulary, domain-specific* interpreter that is genuinely real-time and genuinely impressive, not a general BSL translator — and the difference is stated openly, because a technical judge will probe exactly this.

---

## 2. Problem statement (verified)

- **BSL is a recognised UK language with a sizeable, underserved community.** The British Sign Language Act 2022 (Royal Assent 28 April 2022) legally recognises BSL as a language of England, Scotland and Wales. There are **~151,000 BSL users in the UK, of whom ~87,000 are Deaf** and use BSL as their primary language; BSL has its own grammar and syntax and is **not** a signed form of English, so subtitles/written English are not an adequate substitute for many Deaf people.
- **The hearing-loss population is far larger**: the RNID estimates **1 in 5 UK adults (~12 million) are Deaf or hard of hearing**, rising toward ~14 million by 2035.
- **Interpreter provision is chronically short.** Government and sector reviews repeatedly find a shortage of qualified BSL/English interpreters across England, Scotland and Wales, with sharp geographical variation. The result: Deaf people attend GP, hospital, benefits, housing and social-care appointments **without an interpreter**, relying on note-passing, lip-reading (unreliable), or a family member — with measurably worse outcomes and safeguarding risk.
- **The law creates duty without capacity.** The BSL Act and the Equality Act 2010 create expectations of access, but there is no statutory requirement that every public communication be interpreted, and the interpreter workforce cannot meet demand. Technology that bridges the *unplanned, no-interpreter-available* moment has a clear, real role.

A judge can verify the BSL user count and the Act in under a minute via the BSL Act 2022 explanatory notes and the Government's BSL Report 2022.

---

## 3. Users, use cases, and the ethical frame

### 3.1 Primary user
A Deaf BSL user attending a public-service appointment in London with no interpreter present.

### 3.2 Secondary users
The hearing professional (clinician, housing officer, caseworker); the Deaf user's advocate/family, who receives the record.

### 3.3 Core scenario (demo)
A GP or housing appointment in a high-need London borough. The Deaf user signs; Signbridge speaks their meaning in English; the professional replies in speech; the Deaf user reads live captions. The Policy/Question/Record agents work in the background.

### 3.4 The ethical frame (non-negotiable, and a scoring asset)
- **Augmentation, not replacement.** Signbridge does **not** replace qualified human interpreters for high-stakes, legally binding, or clinical decisions. It is positioned for the gap where no interpreter is available, with that limitation shown to users.
- **Co-design with the Deaf community.** BSL is a living community language; building *for* Deaf people without *involving* them is both ethically wrong and technically doomed (signer variation, regional dialect, register). Credit and consult Deaf signers; ideally recruit a Deaf participant for the demo. State this in the pitch — at a "for impact" event, the team that foregrounds community co-design reads as serious.
- **Signing avatars are contested.** Deaf-led organisations have criticised low-quality signing avatars. The reverse direction (English→BSL) therefore leads with **captions**; any avatar is clearly labelled experimental and secondary.

---

## 4. Why local, why the DGX Spark

### 4.1 Why it must be local
- **Biometric video of a private conversation.** A continuous video stream of a Deaf person communicating about their health, immigration, or safeguarding situation is special-category biometric data. Streaming it to a cloud vision API is a governance non-starter. On-device, the raw video never leaves the room.
- **Latency for turn-taking.** Interpretation must feel conversational. Local inference removes the cloud network round-trip; equally important, sending high-frame-rate video to the cloud would be bandwidth-heavy and laggy.
- **Resilience.** Works in a clinic room or housing office with poor connectivity.

### 4.2 Why the Spark specifically
Signbridge holds an unusually heavy concurrent stack resident at once: a **vision/pose pipeline**, a **sign-recognition model**, a **reasoning/fluency LLM**, **streaming ASR**, **multilingual TTS**, an **embedding model + policy index**, and optionally an **avatar renderer**.

- The Spark's **128 GB coherent unified memory (LPDDR5X)** keeps all of these in one pool with **no PCIe paging** as the pipeline hands off frame→landmarks→signs→text→speech.
- A 24 GB consumer GPU cannot hold a vision pipeline *and* an LLM *and* ASR/TTS resident; it must swap, breaking real-time flow.
- **Honest hardware caveat we design around:** the Spark's ~273 GB/s memory bandwidth makes a single huge (120 B+) LLM slow. Signbridge uses a **moderate LLM (8–32 B)** for disambiguation/fluency — which the hardware runs comfortably — and spends the memory budget on *breadth of concurrent models*, which is the Spark's real strength.

---

## 5. System architecture

### 5.1 High-level diagram

```
 ┌────────────────────── CLIENT (tablet/laptop with camera + mic + screen) ──────────────────────┐
 │  Camera (signer) ─► frames     Mic (hearing person) ─► audio     Screen ─► captions + (avatar)  │
 └───────────────────▲───────────────────────────────────────────────────────────────▼───────────┘
                      │   encrypted WebSocket over LAN (frames/audio up, text/audio/events down)    │
 ┌────────────────────┴──────────────────────────────────────────────────────────────┴───────────┐
 │                            DGX SPARK  (Ubuntu 24.04 ARM64, DGX OS)                               │
 │                                                                                                 │
 │   DEAF ► HEARING (the headline path)                HEARING ► DEAF                               │
 │   ┌───────────────┐  ┌────────────────┐  ┌───────┐  ┌──────────────┐  ┌──────────────────────┐   │
 │   │ Pose/landmark │─►│ Sign recogniser│─►│ LLM   │─►│ ElevenLabs   │  │ ElevenLabs Scribe v2 │   │
 │   │ (MediaPipe)   │  │ (seq model)    │  │fluency│  │ TTS (speech) │  │ ASR → captions       │   │
 │   └───────────────┘  └────────────────┘  └───┬───┘  └──────────────┘  └──────────┬───────────┘   │
 │                                              │                                   │ (opt. avatar) │
 │   ┌──────────────────────── ADVOCACY LAYER (shared with Bridge) ─────────────────▼────────────┐  │
 │   │   Policy Agent (RAG over London borough policy)   │   Question Agent   │   Record Agent    │  │
 │   └──────────────────────────────────────────────────────────────────────────────────────────┘  │
 │                                                                                                 │
 │   SHARED 128 GB UNIFIED MEMORY POOL — vision + LLM + ASR + TTS + embeddings/index, no paging     │
 │   Local encrypted store (record, consent, audit)  ── exported on demand (SAR / appeal) ──►       │
 └─────────────────────────────────────────────────────────────────────────────────────────────────┘
                 NO inference-time egress to the internet (privacy/sovereignty guarantee)
```

### 5.2 The Deaf → hearing path (the headline capability)
1. **Capture & pose extraction.** Camera frames → **MediaPipe Holistic** extracts hand, body, and face landmarks in real time (~30 fps). Working from landmarks (not raw pixels) is faster, more robust to background/lighting, and inherently more privacy-preserving.
2. **Sign recognition.** A lightweight sequence model (Transformer or BiLSTM over the landmark stream) maps signing to a stream of recognised sign tokens / glosses over a **constrained, domain-specific vocabulary** (see §6 and §10).
3. **Fluency via LLM.** Recognised sign tokens are often telegraphic and order-different from English. An LLM converts the token/gloss stream into fluent English, using conversational context — an approach validated by recent work on **LLM-based sign-spotting disambiguation**. This is also where fingerspelling (spelled names, postcodes) is reassembled.
4. **Speech out.** **ElevenLabs multilingual TTS (on-device)** speaks the English aloud, streamed for low latency.

### 5.3 The hearing → Deaf path
- **ElevenLabs Scribe v2 (on-device)** transcribes the professional's speech in real time → **live captions** on the Deaf user's screen (primary, reliable).
- **Experimental:** an optional signing-avatar render of key phrases, clearly labelled as experimental and secondary (see §3.4).

### 5.4 The advocacy layer (reused from Bridge)
- **Policy Agent** — RAG over the borough/trust policy corpus; surfaces the relevant entitlement with a citation as the conversation unfolds.
- **Question Agent** — prompts the Deaf user with high-value questions they didn't think to ask.
- **Record Agent** — produces a timestamped, structured, citation-backed record (English transcript both directions, policies cited, commitments, next steps) usable for appeals, ombudsman complaints, and SARs. **Lead the demo on this — it's the most defensible feature.**

### 5.5 Orchestration
A lightweight `asyncio` event bus carries `frame`, `landmarks`, `sign_token`, `gloss_sequence`, `english_utterance`, `tts_audio`, `caption`, `policy_card`, `question_prompt`, `commitment`. Keep the real-time vision→speech loop hand-rolled for latency control; optionally wrap the non-real-time advocacy agents in **NVIDIA NeMo Agent toolkit / NemoClaw** for sponsor alignment.

---

## 6. Model selection and rationale

| Role | Primary choice | Notes |
|---|---|---|
| Pose/landmark extraction | **MediaPipe Holistic** | Real-time hands+pose+face landmarks on a webcam; robust, light, the standard SLR front-end. |
| Sign recogniser | Custom lightweight **Transformer/BiLSTM over landmarks**, trained on a constrained vocabulary the team records; or a pre-trained sign-spotting model where licence allows | Isolated/short-phrase recognition over a bounded vocabulary is real-time and >90% achievable; general continuous translation is **not** a weekend deliverable. |
| Fluency / disambiguation LLM | **Qwen2.5-14B / Llama 3.1 8B** (fast) | Converts telegraphic gloss stream → fluent English; handles context and fingerspelling reassembly. |
| Advocacy reasoning LLM | **Qwen2.5-32B / Llama 3.3 70B** (async) | Policy reasoning; latency-tolerant (background cards). Optional dual-LLM (fast + large) as in Bridge. |
| ASR (reverse) | **ElevenLabs Scribe v2 (on-device)** | ~150 ms p50 streaming; diarization + timestamps feed the Record Agent. |
| TTS (speech out) | **ElevenLabs multilingual (on-device)** | Expressive English voice; on-device keeps everything in-box. |
| Embeddings | BGE-M3 / e5-large | Policy retrieval. |
| Signing avatar (experimental) | Pre-built research avatar or skip | Lead with captions; avatar clearly secondary. |

### 6.1 Datasets and the BOBSL caveat
The principal BSL research dataset is **BOBSL (BBC-Oxford, ~1,400 hours, 37 signers)**, with a derived **continuous-recognition benchmark (BOBSL-CSLR, ~5,000-sign vocabulary)**. **BOBSL video requires a BBC terms-of-use agreement and is non-commercial research-licensed**, so it is not something to "just download and train on" in a weekend. The pragmatic weekend approach is to **record your own clips for a curated ~50–150-sign domain vocabulary** (with Deaf collaborators), train/fine-tune the small landmark sequence model on those, and use the LLM for fluency. Cite BOBSL/CSLR2 as the production training path.

---

## 7. Memory and latency budgets

### 7.1 Memory budget (fits 128 GB with wide headroom)

| Component | Approx. resident size |
|---|---|
| MediaPipe pose pipeline + frame buffers | ~1–2 GB |
| Sign-recognition sequence model | ~0.5–3 GB |
| Fluency LLM 8–14 B | ~6–10 GB |
| Advocacy LLM 32–70 B @ 4-bit (optional, async) | ~20–40 GB |
| ASR (Scribe v2) | ~2–4 GB |
| TTS (multilingual) | ~2–5 GB |
| Embeddings + policy index (one borough) | ~2–6 GB |
| Avatar renderer (optional) | ~2–5 GB |
| OS + app + buffers | ~8–12 GB |
| **Total** | **~45–85 GB** |

The point for judges: a vision pipeline *and* one-to-two LLMs *and* ASR *and* TTS resident at once — the unified-memory advantage made concrete.

### 7.2 Latency budget (honest, streaming)

| Stage | Target |
|---|---|
| Camera + MediaPipe landmarks | ~30–50 ms / frame (real-time 30 fps) |
| Sign recognition over a phrase window | ~50–150 ms |
| Phrase segmentation (waiting for a complete sign phrase) | variable — the main perceived latency |
| LLM fluency (time-to-first-token) | ~100–300 ms |
| TTS time-to-first-audio | ~100–200 ms |
| **Perceived signing → spoken English (start)** | **~0.6–1.5 s after a complete phrase** |

**Be precise in the pitch:** the inherent latency in sign translation is *phrase segmentation* — you must observe a complete sign unit before translating, exactly as a human interpreter lags the signer. Pitch it as "near-real-time, interpreter-like cadence," not "instant," and note that local inference removes the cloud round-trip on top of that.

---

## 8. Data foundation (satisfying the hard London-open-data requirement)

A vision product satisfies the London-open-data requirement through its **advocacy and targeting layers**, not the recognizer:

- **ONS Census 2021 disability / hearing data by London borough** (via London Datastore / ONS) — establishes where Deaf/hard-of-hearing residents are concentrated, drives deployment prioritisation, and frames impact. *(Confirm the exact census table for hearing impairment / disability by borough before citing a figure.)*
- **London Datastore health and accessibility datasets** — service provision, deprivation overlays.
- **Borough/trust policy corpus** (demo: one borough, one domain) — the Policy Agent's retrieval base, identical in structure to Bridge.

This gives the project a genuine London-open-data foundation while keeping the recognizer focused on BSL. State this tie explicitly so judges see the requirement is met by design, not bolted on.

---

## 9. Integrations required

| Integration | Purpose | Access plan |
|---|---|---|
| **MediaPipe** | Real-time landmark extraction | Open-source; runs on client or Spark. |
| **ElevenLabs on-device** (Scribe v2 + TTS) | Speech out + captions in, kept on-box | Ask ElevenLabs reps at the event for on-device/enterprise access day one; cloud fallback (zero-retention + EU residency) only if needed — but the offline proof then requires local open ASR/TTS. |
| **Ollama / NVIDIA NIM** | Serve LLMs locally (ARM64) | Standard on Spark. |
| **Vector DB** — Qdrant / LanceDB (local) | Policy retrieval | Local container. |
| **Sign data** | Train the constrained recognizer | Record own clips with Deaf collaborators; BOBSL/CSLR2 as production path (BBC licence required). |
| **NeMo Agent toolkit / NemoClaw** (optional) | Orchestrate advocacy agents | Sponsor-aligned. |
| **WebSocket / WebRTC** | Low-latency frame + audio transport | Self-hosted; no third party. |
| **London Datastore / ONS** | Targeting + policy corpus | Public download; ingest before demo. |

---

## 10. Infrastructure and deployment

- **Compute:** 1× DGX Spark (GB10, 128 GB unified), DGX OS / Ubuntu 24.04 **ARM64**.
- **Runtime:** Docker (ARM64/NGC images); Ollama for LLMs; ElevenLabs on-device container; vector DB; FastAPI + WebSocket backend; MediaPipe (client-side or Spark-side).
- **Where the vision runs:** prefer running MediaPipe **on the client** to send compact landmark vectors (not raw video) to the Spark — lighter on the network and even more privacy-preserving. Recognition + LLM + TTS run on the Spark.
- **Build-time access:** NVIDIA Sync or SSH (`dgx-spark.local`); SSH port-forwarding to reach the backend from laptops.
- **Demo network:** a dedicated travel router (or the Spark's hotspot) so you control the LAN and can cleanly perform the offline proof. Client camera/mic device on the same LAN.
- **No inference-time internet dependency.** All models, data, and the policy corpus are loaded before the demo.

---

## 11. Tech stack (concrete)

- **Vision:** MediaPipe Holistic; PyTorch (ARM64) for the landmark sequence model; OpenCV for capture.
- **Backend:** Python 3.11, `asyncio`, FastAPI, `websockets`.
- **Inference:** Ollama (LLMs), ElevenLabs on-device SDK/container (ASR+TTS), `sentence-transformers`/BGE-M3.
- **Vector store:** Qdrant or LanceDB (local).
- **Client:** React/Next.js PWA; Web Camera + Web Audio APIs; WebSocket streaming; a large, calm caption display and an "agent activity" strip.
- **Record output:** structured JSON → PDF/HTML.

---

## 12. Security, privacy and governance

- **Legal frame:** UK GDPR + DPA 2018; special-category **biometric** data (video of a person). A real deployment needs a **DPIA**; say so.
- **Data flow:** camera → (ideally) client-side landmark extraction → encrypted LAN transport of landmark vectors → on-Spark recognition/LLM/TTS in memory → record written only on consent → encrypted local store → exported on demand. **No raw video, and no inference-time egress, leave the room.**
- **Consent:** explicit consent at session start; the Deaf user controls whether a record is kept.
- **Retention:** ephemeral by default; record under a configurable, public-body-controlled retention policy.
- **Auditability:** every policy claim carries a source + timestamp via the Record Agent.
- **Safety/ethics positioning:** augmentation not replacement; co-designed with Deaf users; avatar output labelled experimental; never presented as a certified interpreter for binding decisions.

---

## 13. Client UX and the demo device

- **Form factor:** a tablet/laptop on the desk with a camera facing the Deaf user and a screen they can read; the Spark is the engine under the table.
- **Deaf user's view:** large, calm live captions of the hearing person's speech; optional avatar; their own recognised-meaning shown back for confirmation ("Is this what you meant?") — a respectful correction loop.
- **Professional's view:** the spoken English plus live Policy cards and Question prompts.
- **Agent activity strip:** subtle real-time trace of vision → recognition → fluency → speech, plus the advocacy agents — the visual proof of the concurrent multi-model system (design = a full quarter of the score).

---

## 14. Demo plan (≈3 minutes)

1. **Frame (15s):** "151,000 people use BSL; there aren't remotely enough interpreters, so Deaf Londoners face the GP and the housing office alone. Watch this — and everything runs on this box, nothing leaves the room." (Point at the Spark.)
2. **The headline moment (60s):** a Deaf signer (ideally a Deaf collaborator) signs a scripted GP/housing exchange over the constrained domain vocabulary; the room hears fluent English ~a second later. This is the jaw-drop.
3. **Reverse + confirmation (30s):** the professional speaks; live captions appear for the Deaf user; the "is this what you meant?" confirmation loop shows respect for accuracy.
4. **Advocacy beat (30s):** a Policy card surfaces an entitlement with its source; the Question Agent prompts a missed question.
5. **Offline proof (20s):** pull the network. It keeps working. "No video of this conversation ever left the room."
6. **The record (25s):** one tap → a bilingual, citation-backed, appeal-ready record.
7. **Close (10s):** one line on co-design with the Deaf community and the production path (BOBSL-scale training, full continuous translation).

**Backup:** pre-recorded signing clips and a canned path, in case live recognition misfires under demo lighting — rehearse the fallback.

---

## 15. Build plan (weekend)

| When | Goal | Owners (team of 4–5) |
|---|---|---|
| **Fri eve** | Spark setup (first boot via monitor+keyboard+ethernet); env/containers; Ollama models; ElevenLabs access decision; **record the domain sign vocabulary with Deaf collaborator(s)**; MediaPipe capture working | All; 1 infra lead |
| **Sat AM** | Train/fine-tune the landmark sequence model on the recorded vocabulary; baseline recognition accuracy | 2 on vision |
| **Sat PM** | Gloss→fluent-English LLM step; ElevenLabs TTS out; first end-to-end Deaf→hearing path | 1 vision, 1 LLM/voice |
| **Sat eve** | Reverse path (Scribe → captions); confirmation loop; client UI | 1 ASR, 1 frontend |
| **Sun AM** | Advocacy layer (reuse Bridge): Policy/Question/Record over one-borough corpus; offline-proof rehearsal | 2 |
| **Sun midday** | Polish, lighting/camera setup for the demo, rehearse x3 with the canned fallback ready | All |

---

## 16. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Live recognition misfires (lighting, signer variation, camera angle) | **High** | Constrain vocabulary; record training clips in demo conditions; lock demo lighting/background; canned-clip fallback. |
| Over-claiming general BSL translation | High (credibility) | State the constrained-vocabulary scope openly; frame full translation as roadmap; cite BOBSL as the production path. |
| BOBSL licence / no time to train at scale | High | Don't depend on BOBSL for the weekend; train small on self-recorded vocabulary. |
| Signing-avatar quality offends/underwhelms | Medium | Lead with captions; label avatar experimental; foreground Deaf co-design. |
| On-device ElevenLabs access not granted | Medium | Local open ASR/TTS (Whisper + Kokoro/Piper) so the offline proof holds; ElevenLabs as quality showcase. |
| Latency feels laggy | Medium | Stream; segment on complete phrases; explain interpreter-like lag; fast LLM in the loop. |
| ARM64 dependency friction | Medium | NVIDIA containers + Ollama; resolve Friday night. |
| Ethical misstep (building "about" Deaf people without them) | Medium (reputational) | Recruit/credit Deaf collaborators; positioning as augmentation; humility in the pitch. |

---

## 17. How Signbridge maps to the judging rubric

- **Technical implementation:** a real-time vision pipeline + LLM + ASR + TTS concurrent on-device — the most technically ambitious use of the hardware in the room. Strong (if it works).
- **Design / UX:** the live signing→speech moment, the caption view, the confirmation loop, the agent-activity strip. Highest spectacle of any option.
- **Potential impact:** 87,000 Deaf BSL users + 12 million hard-of-hearing; the unplanned-no-interpreter gap is real and verifiable.
- **Quality / creativity:** rarely attempted, highly distinctive; the advocacy layer + Record Agent differentiate it from a "gesture demo."
- **ElevenLabs "Best Use of Voice":** voice is the literal output of interpretation; Scribe v2 + multilingual TTS on-device. Strong fit.

**Net:** the highest ceiling of the shortlist and the best "wow," carrying the highest chance of a demo that doesn't fire. Win condition = ruthless vocabulary scoping + a rehearsed fallback + foregrounded Deaf co-design.

---

## 18. Roadmap (post-hackathon)

- Train at scale on BOBSL/CSLR2 toward signer-independent continuous translation.
- Formal co-design and evaluation with Deaf-led organisations; community-sourced regional-dialect data.
- Robust English→BSL production (only if Deaf users want it; current avatars are weak).
- Integration with public-body case-management; DPIA and a pilot in a high-need borough.
- Fingerspelling and number/postcode robustness; multi-signer scenes.

---

## 19. Sources / references

- British Sign Language Act 2022 (legislation.gov.uk explanatory notes: ~90,000 primary BSL users, ~150,000 signers; England/Scotland/Wales).
- UK Government, *The British Sign Language (BSL) Report 2022* (~151,000 BSL users, ~87,000 Deaf; RNID 1-in-5 / 12 million hard of hearing).
- Government / sector market reviews on the BSL interpreter shortage.
- Oxford VGG **BOBSL** dataset and **BOBSL-CSLR / CSLR2** benchmark (BBC terms of use; ~1,400 hours; ~5,000-sign continuous benchmark).
- Sign-language recognition literature: MediaPipe/YOLO real-time isolated recognition (>90% on bounded sets); Sign Language Transformers; LLM-based sign-spotting disambiguation (2025); signer-independent accuracy gap.
- NVIDIA DGX Spark documentation (GB10, 128 GB unified LPDDR5X ~273 GB/s, Ubuntu 24.04 ARM64, NVIDIA Sync, Ollama).
- ElevenLabs on-device deployment (April 2026), Scribe v2 Realtime, EU residency, zero-retention.
- London Datastore / ONS Census 2021 (London borough disability/hearing data; policy corpus).

*Verify the London borough hearing/disability figure and re-confirm model accuracy/latency claims immediately before the pitch.*
