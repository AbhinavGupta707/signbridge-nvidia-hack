# Signbridge Rehearsal Checklist

## Before First Rehearsal

- [ ] Scenario is locked to housing repair / damp and mould.
- [ ] Vocabulary is locked to the phrase table in `demo/RUNBOOK.md`.
- [ ] Vision team has 5-10 takes per must-have phrase or an explicit limitation.
- [ ] Every clip has consent status, token label, signer ID/pseudonym, and lighting note.
- [ ] Policy cards use local copies of sources with URL and retrieval date.
- [ ] The UI visibly says "Constrained housing-repair demo. Not certified interpretation."
- [ ] Record export is consent-gated.
- [ ] Fallback modes are rehearsed without apology.

## Technical Preflight

- [ ] Client can reach local server over the private LAN.
- [ ] `/health` or equivalent shows orchestrator, vision, voice, advocacy, and record state.
- [ ] Camera view has hands, face, and torso in frame.
- [ ] Microphone captions are readable from judge distance.
- [ ] TTS volume is audible but not jarring.
- [ ] Policy card appears for damp/mould and cites a real source.
- [ ] Question Agent emits only one practical question at a time.
- [ ] Record export opens and includes transcript, accepted/corrected translations, policy sources, commitments, and next steps.
- [ ] Offline proof is tested by removing WAN/external egress, not by disconnecting the local LAN.

## Timing Run

- [ ] 0:00-0:18 opening delivered without extra stats.
- [ ] 0:18-0:32 consent shown.
- [ ] 0:32-1:08 sign-to-speech works or Level 1 fallback is triggered.
- [ ] 1:08-1:28 speech-to-captions works or labelled caption fallback is triggered.
- [ ] 1:28-1:56 policy card and question prompt appear.
- [ ] 1:56-2:24 follow-up question is spoken and captioned.
- [ ] 2:24-2:42 offline proof runs.
- [ ] 2:42-2:55 record export and close.
- [ ] Full run is under 3:20 including fallback.

## Presenter Guardrails

- [ ] Say "constrained phrase recognition" at least once.
- [ ] Say "augmentation, not replacement" in the close.
- [ ] Say "not a certified interpreter" if the judge has not already seen the limitation label.
- [ ] Say "no raw video leaves the room," not "no video exists."
- [ ] If Deaf collaborator was involved, credit them specifically and respectfully.
- [ ] If no Deaf collaborator was involved, state that production requires paid Deaf-led co-design and that prototype data is a limitation.
- [ ] Do not cite numbers that are not in `demo/SOURCES_AND_IMPACT_NOTES.md`.

## Vision Team Handoff

- [ ] Must-have tokens recorded: `CONSENT_RECORD_YES`, `NEED_BSL_INTERPRETER`, `MY_HOME_DAMP_MOULD`, `MOULD_CHILD_BEDROOM`, `CHILD_ASTHMA_WORSE`, `URGENT_REPAIR`, `REPORTED_BEFORE`, `PHOTO_EVIDENCE`, `ASK_INSPECTION_DATE`, `ASK_WRITTEN_CONFIRMATION`, `ASK_TEMPORARY_ACCOMMODATION_IF_UNSAFE`, `PLEASE_SEND_EMAIL_TEXT`, `PHONE_NOT_ACCESSIBLE`, `MAKE_RECORD`, `STOP_REPEAT`, `I_DO_NOT_UNDERSTAND`.
- [ ] Confusion pairs checked: `ASK_INSPECTION_DATE` vs `ASK_WRITTEN_CONFIRMATION`; `URGENT_REPAIR` vs `REPORTED_BEFORE`; `MAKE_RECORD` vs `NO_RECORD`.
- [ ] Recognition threshold set before judging.
- [ ] Low-confidence UI path tested.
- [ ] Level 1 clips and Level 2 landmark replay are one click away.

## Source Claim Check

- [ ] GOV.UK BSL Report 2022 claim checked: BSL Act recognition, 151,000 BSL users, 87,000 Deaf users, RNID 1 in 5 / 12 million.
- [ ] GOV.UK Locked Out 2025 claim checked: public-service barriers, interpreter shortage, access failures, cost range if used.
- [ ] City of London Damp and Mould Policy claim checked: seven-working-day inspection, records, six-month follow-up.
- [ ] GOV.UK Awaab's Law claim checked: social-housing emergency/significant damp and mould timeframes.
- [ ] City of London regulatory judgement checked: C3, repairs/maintenance serious failings, 18% Decent Homes figure if used.
- [ ] NVIDIA DGX Spark spec checked: 128 GB coherent unified memory and 273 GB/s bandwidth.
- [ ] ElevenLabs activation state checked by registration/discovery/install/official activation flow before debugging runtime.

## Final Rehearsal Acceptance

- [ ] Demo works twice in a row at the judging table or equivalent lighting.
- [ ] Fallback transition has been rehearsed once.
- [ ] Q&A owner has `demo/PITCH.md` open.
- [ ] Operator has `demo/FALLBACKS.md` open.
- [ ] Presenter can answer "Is this general BSL translation?" in one sentence: "No, this is constrained housing-repair phrase recognition; general BSL translation is a Deaf-led production roadmap, not our hackathon claim."

