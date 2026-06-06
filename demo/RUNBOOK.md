# Signbridge 3-Minute Demo Runbook

## Roles

- Presenter: owns the narrative, judge-facing caveats, and timing.
- Signer: signs only the locked demo phrases. Ideally this is a Deaf collaborator; if not, say the clips are prototype team-member data and production requires Deaf-led data collection.
- Housing officer: speaks the scripted professional replies.
- Operator: watches confidence, triggers fallback if needed, exports the record, and handles offline proof.

## Pre-Demo State

- App is open to the interpreter screen, not a landing page.
- Visible limitation label: "Constrained housing-repair demo. Not certified interpretation."
- Session scenario is `housing_repair`.
- Consent state is visible. Record export is off until the user consents.
- Policy corpus is loaded locally: City of London Damp and Mould Policy, GOV.UK Awaab's Law guidance, City of London regulatory judgement, BSL impact sources.
- Local fallback voice path is ready. If ElevenLabs on-device is officially activated, use it; otherwise keep any ElevenLabs API voice as an online quality mode only and use local fallback for offline proof.
- Offline proof method is ready: unplug WAN / block external egress, but keep the private LAN between client and DGX Spark / ZGX Nano alive.

## Timed Demo

Target: 2:55. Hard stop: 3:20.

### 0:00-0:18 - Frame

Presenter:

"This is Signbridge. It is for the moment a Deaf BSL user is in a public-service appointment and no qualified interpreter is available. We are showing a constrained housing-repair vocabulary today, not general BSL translation. The point is local, consent-based communication support: no raw video of this conversation leaves the room."

Operator:

- Start session.
- Show `system.status` ready states.

### 0:18-0:32 - Consent and Scope

Signer signs: `CONSENT_RECORD_YES`

Expected spoken output:

"I consent to keeping a record of this appointment."

Presenter:

"The user controls whether the record exists. We show the recognised meaning back before it is accepted."

### 0:32-1:08 - Headline Sign-to-Speech Moment

Signer signs, in this order:

1. `NEED_BSL_INTERPRETER`
2. `MY_HOME_DAMP_MOULD`
3. `MOULD_CHILD_BEDROOM`
4. `CHILD_ASTHMA_WORSE`
5. `URGENT_REPAIR`

Expected recognised token group:

`["NEED_BSL_INTERPRETER","MY_HOME_DAMP_MOULD","MOULD_CHILD_BEDROOM","CHILD_ASTHMA_WORSE","URGENT_REPAIR"]`

Expected spoken output:

"I use BSL. There is damp and mould in my home, including my child's bedroom. My child's asthma is worse, and I need this treated as urgent."

Presenter:

"The camera path is landmarks to constrained phrase recognition to a local language model for fluency. The language model is not allowed to add facts."

### 1:08-1:28 - Speech-to-Captions

Housing officer says:

"I understand. I can book an inspection, and I will send the appointment time in writing."

Expected caption:

"I understand. I can book an inspection, and I will send the appointment time in writing."

Presenter:

"The reverse path leads with captions. We are deliberately not leading with a signing avatar, because poor avatars are a real concern in Deaf communities."

### 1:28-1:56 - Policy and Question Agent

Expected policy card 1:

Title: "Damp and mould: inspection and records"  
Claim: "City of London policy says reports of suspected damp, mould or condensation should lead to a property inspection within seven working days, with records kept of damp and mould cases and actions taken."  
Source: City of London Damp and Mould Policy PDF

Expected policy card 2 if available:

Title: "Awaab's Law: urgent health risk"  
Claim: "For social housing, significant damp and mould hazards have fixed investigation and safety timeframes; emergency hazards require action within 24 hours."  
Source: GOV.UK Awaab's Law guidance

Expected question prompt:

"Ask for the inspection date, the written repair plan, and what happens if the home cannot be made safe in time."

Presenter:

"This is why it is more than translation. The user gets an entitlement card and a practical next question, both tied to sources."

### 1:56-2:24 - Follow-Up Question

Signer signs:

1. `ASK_INSPECTION_DATE`
2. `ASK_WRITTEN_CONFIRMATION`
3. `ASK_TEMPORARY_ACCOMMODATION_IF_UNSAFE`

Expected spoken output:

"When will the inspection happen, will you confirm the repair plan in writing, and what happens if the home cannot be made safe in time?"

Housing officer says:

"I will put the inspection date, repair plan, and follow-up steps in the record now."

Expected caption:

"I will put the inspection date, repair plan, and follow-up steps in the record now."

### 2:24-2:42 - Offline Proof

Operator:

- Unplug WAN or toggle the prepared egress block.
- Do not disconnect the client from the local LAN.
- Keep one short clip/live phrase running.

Presenter:

"Now we remove external internet. The private LAN still connects the tablet to the box, but inference and retrieval stay local: recogniser, language model, policy index, voice fallback, and record. This is the privacy claim made visible."

Signer signs:

`PLEASE_SEND_EMAIL_TEXT`

Expected spoken output:

"Please send updates by email or text; phone calls are not accessible to me."

### 2:42-2:55 - Record Export and Close

Operator:

- Trigger `record.export`.
- Show `record.exported` or the exported HTML/PDF.

Presenter:

"One tap exports a timestamped record: accepted translations, captions, policy sources, questions, commitments, and next steps. Signbridge is augmentation, not replacement. It covers the unplanned gap with consent, citations, and user control; production must be Deaf-led."

## Exact Vision-Team Phrase Set

Record 5-10 takes per phrase in demo lighting. If a Deaf collaborator is available, let them choose the natural BSL form; labels below are intent labels for the recogniser, not instructions to force English word order.

### Minimum Live Path

| Token label | Intended meaning for TTS | Demo priority |
|---|---|---|
| `CONSENT_RECORD_YES` | I consent to keeping a record of this appointment. | Must |
| `NEED_BSL_INTERPRETER` | I use BSL / I need BSL communication support. | Must |
| `MY_HOME_DAMP_MOULD` | There is damp and mould in my home. | Must |
| `MOULD_CHILD_BEDROOM` | The mould is in my child's bedroom. | Must |
| `CHILD_ASTHMA_WORSE` | My child's asthma / breathing is worse. | Must |
| `URGENT_REPAIR` | I need this treated as urgent. | Must |
| `REPORTED_BEFORE` | I reported this before. | Must |
| `PHOTO_EVIDENCE` | I have photos as evidence. | Must |
| `ASK_INSPECTION_DATE` | When will the inspection happen? | Must |
| `ASK_WRITTEN_CONFIRMATION` | Will you confirm the repair plan in writing? | Must |
| `ASK_TEMPORARY_ACCOMMODATION_IF_UNSAFE` | What happens if the home cannot be made safe in time? | Must |
| `PLEASE_SEND_EMAIL_TEXT` | Please send updates by email or text. | Must |
| `PHONE_NOT_ACCESSIBLE` | Phone calls are not accessible to me. | Must |
| `MAKE_RECORD` | Please keep / export the record. | Must |
| `STOP_REPEAT` | Stop / please repeat that. | Must |
| `I_DO_NOT_UNDERSTAND` | I do not understand. | Must |

### Nice-To-Have Phrases

| Token label | Intended meaning for TTS |
|---|---|
| `NO_RECORD` | Do not keep a record. |
| `NEED_MORE_TIME` | I need more time. |
| `PLEASE_SLOW_DOWN` | Please slow down. |
| `CONTACT_ADVOCATE` | Please contact my advocate. |
| `COMPLAINT_ROUTE` | I want to know how to complain or escalate. |
| `FOLLOW_UP_SIX_MONTHS` | Will you follow up after the repair? |
| `REASONABLE_ADJUSTMENT_CAPTIONS` | Please keep captions on as a reasonable adjustment. |
| `THANK_YOU` | Thank you. |

### Vision Safety Notes

- Do not expand past this set until the demo path works twice in a row.
- Use a confidence threshold; below threshold, trigger confirmation or fallback instead of speaking a guessed meaning.
- Preserve uncertainty in output: "I think you said..." is better than a confident wrong statement.
- Keep child/asthma as a tenant-reported vulnerability for housing prioritisation. Do not turn it into medical advice.

