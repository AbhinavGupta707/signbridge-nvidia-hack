# Signbridge Pitch, Ethics, and Judge Q&A

## 20-Second Opening

"This is Signbridge: a local-first communication bridge for the moment a Deaf BSL user is in a public-service appointment and no qualified interpreter is available. Today we are not claiming general BSL translation. We are showing a constrained housing-repair vocabulary for damp and mould, with captions back to the Deaf user, source-backed policy prompts, and a consent-gated record."

## 10-Second Close

"Signbridge is augmentation, not replacement. It covers an unplanned gap with local privacy, user confirmation, citations, and a record the user controls. Production has to be Deaf-led."

## Ethical Positioning

Signbridge should be framed as communication support in a documented service gap. It is not a certified interpreter, not a substitute for qualified BSL/English interpreters, and not appropriate for high-stakes legal, safeguarding, police, immigration, or clinical decision-making without a human professional.

The demo earns trust by being explicit:

- BSL is a full language with its own grammar, not signed English.
- The hackathon recogniser is constrained to a housing repair phrase set.
- The Deaf user confirms recognised meaning before it enters the record.
- Captions are the primary hearing-to-Deaf path; any avatar is secondary and experimental.
- Raw video is not retained and does not leave the room.
- Records are consent-gated and source-backed.
- Production requires Deaf-led co-design, paid Deaf collaborators, broader signer coverage, licensed data, governance, and evaluation.

## Augmentation, Not Replacement

Use this exact answer when challenged:

"We are not replacing interpreters. A qualified interpreter is the correct answer for planned, complex, legal, clinical, or high-stakes appointments. Signbridge is for the unplanned gap: the user is already in the room, no interpreter is available, and the alternative is often notes, lip-reading, a family member, or no meaningful access. We make that moment safer by constraining the domain, asking for confirmation, keeping the record under user control, and citing sources."

## Likely Judge Questions

### Is this general BSL translation?

No. This is constrained public-service phrase recognition for one housing repair scenario. The recogniser only covers the locked vocabulary in the runbook. Full BSL translation would require Deaf-led co-design, much larger licensed datasets, regional variation coverage, signer-independent evaluation, and clinical/legal governance before high-stakes use.

### Why is this not just captions?

Captions help the Deaf user read the hearing professional's speech. They do not let a BSL-first Deaf user express themselves naturally to the room. Signbridge covers both directions: signed intent to spoken English, and speech back to captions.

### What prevents hallucination?

The demo path is constrained. The recogniser emits known token labels and confidence. The fluency model is instructed to translate only those tokens, not add facts, dates, symptoms, commitments, legal advice, or medical claims. Low confidence triggers confirmation or fallback.

### What runs locally?

The target offline path is local camera/landmarks, constrained recogniser, local LLM fluency, local policy index, local record export, and local ASR/TTS fallback. If ElevenLabs on-device is officially activated, it can be part of that path. If not, ElevenLabs API can be shown only as an online quality mode, with the offline proof using local fallback.

### Why does this need DGX Spark / ZGX Nano?

The value is concurrent local inference: vision landmarks, sequence recognition, an LLM, ASR, TTS, embeddings, retrieval, and record generation all resident together. NVIDIA DGX Spark materials list Grace Blackwell, 128 GB coherent unified memory, 273 GB/s memory bandwidth, 4 TB NVMe, and 10 GbE, which fit this local multi-model workflow.

### Is raw video stored?

No for the demo. The camera sees video, but the product path sends compact landmark events to the local box and does not retain raw video. The exported record contains accepted text, captions, policy cards, commitments, and source URLs after consent.

### How do you handle privacy law?

We treat signing video as highly sensitive biometric data. A production public-body deployment would need a DPIA, retention policy, audit model, access controls, procurement review, and Deaf/community governance. The hackathon demo shows the intended privacy shape: local inference, no inference-time egress, consent-gated records.

### What if the recogniser is wrong?

Wrong is expected sometimes, especially with signer variation and lighting. That is why the UI shows confidence and asks "Is this what you meant?" The record stores accepted or corrected meaning. Below threshold, the operator switches to clip, landmark, or scripted replay rather than letting the system guess.

### Why housing and damp/mould?

It is concrete, demonstrable, and sourceable. City of London has a damp and mould policy with inspection, resident support, record-keeping, and follow-up points. GOV.UK Awaab's Law guidance provides current social-housing repair timeframes. The 25 February 2026 City of London regulatory judgement makes repairs and tenant accountability a live local public-service issue.

### Are you giving legal advice?

No. Policy cards are source-backed information prompts, not legal advice. They help the user ask a better question and leave with a record. Any formal complaint, legal action, safeguarding issue, or clinical decision still requires the appropriate human professional.

### What about Deaf co-design?

It is required. If a Deaf collaborator was involved in the demo, credit them and say what they shaped. If not, say: "This prototype uses team-member clips to prove the architecture. That is a limitation, not a production data strategy. The production path is paid Deaf-led co-design and evaluation."

### What is the measurable demo win?

At least 10 scripted signed phrases produce accepted spoken English in demo conditions; speech back appears as captions or a labelled fallback; at least one source-backed policy card appears; one practical question prompt appears; the record exports; and the offline proof works without external internet.

## Language To Avoid

- "Universal translator"
- "Certified interpreter"
- "Understands BSL"
- "Works for any signer"
- "Medical triage"
- "Legal advice"
- "No risk"
- "Fully offline with ElevenLabs" unless activation has been proven

## Language To Use

- "Constrained phrase recognition"
- "Domain-specific public-service vocabulary"
- "BSL-first user"
- "Confirmation loop"
- "Local-first privacy"
- "Source-backed policy card"
- "Consent-gated record"
- "Augmentation, not replacement"

