# Signbridge Demo Fallback Ladder

The fallback should feel like an honest reliability mode, not a failure. Use the same UI, same event contract, same record, and same policy cards whenever possible.

## Operator Rule

If a critical phrase confidence is below 0.70, do not let it speak as fact. Trigger confirmation, switch input mode, or move down the ladder.

Critical phrases:

- `MY_HOME_DAMP_MOULD`
- `MOULD_CHILD_BEDROOM`
- `CHILD_ASTHMA_WORSE`
- `URGENT_REPAIR`
- `ASK_INSPECTION_DATE`
- `ASK_WRITTEN_CONFIRMATION`
- `ASK_TEMPORARY_ACCOMMODATION_IF_UNSAFE`

## Ladder

### Level 0 - Live Camera Recognition

Use when:

- Lighting is stable.
- Hands are fully in frame.
- Confidence is 0.70+ for critical phrases and 0.60+ for non-critical phrases.

Narration:

"This is the live path: camera to landmarks, landmarks to constrained sign intent, local fluency, then speech."

### Level 1 - Prerecorded Clips Through Recogniser

Use when:

- Live camera angle or judge table lighting causes misses.
- Recogniser works on controlled clips.

Operator action:

- Trigger approved clip replay through the same landmark and recognition path.
- Keep the app limitation label visible.

Narration:

"For judging-room reliability, I am switching to our locked clips from the same phrase set. These clips still go through the recogniser; this is not a video playback of the output."

### Level 2 - Precomputed Landmarks Through Recogniser

Use when:

- MediaPipe/camera capture is unstable.
- Recogniser works on saved landmark files.

Operator action:

- Replay precomputed landmark events as `landmark.frame`.
- Let recogniser emit `recognition.final`.

Narration:

"This mode removes the camera dependency but keeps the privacy architecture: the backend receives landmark vectors, not raw video, and the recogniser still decides the phrase."

### Level 3 - Scripted Event Replay

Use when:

- Vision stack is unavailable.
- Need to preserve the end-to-end story: captions, policy, question, record, offline proof.

Operator action:

- Trigger `demo.replay` for the housing scenario.
- Make it clear this is a scripted replay.

Narration:

"I am switching to scripted event replay so you can inspect the full product loop. The vision path is isolated here; the rest of the system is the same UI contract: translation, captions, policy cards, questions, and record export."

### Level 4 - UI-Only Walkthrough

Use only if the backend is down.

Narration:

"We are in UI walkthrough mode. I will not pretend the live pipeline is running. What I can show is the intended appointment workflow, safety copy, source cards, confirmation, and record shape."

## Fallback Branches By Failure

| Failure | First response | Next response |
|---|---|---|
| Recognition wrong but camera is stable | Ask for confirmation / repeat | Level 1 clips |
| MediaPipe/camera blank | Level 2 landmarks | Level 3 replay |
| TTS unavailable | Use text output plus local system voice | Continue demo, say voice fallback is active |
| ASR unavailable | Use typed/canned professional reply captions | Continue demo, label reverse-path fallback |
| Policy retrieval down | Show cached source card | Continue record export with cached source URL |
| Record export down | Show live record panel | Offer exported JSON/HTML after demo |
| Internet disconnect breaks voice | Switch to local TTS/ASR fallback | Say ElevenLabs API was online quality mode only |
| Full backend down | Level 4 UI-only | Keep Q&A focused on architecture and ethics |

## Offline Proof Variants

### Preferred

- WAN unplugged or firewall blocks external egress.
- Local LAN stays up.
- Local recogniser, local LLM, local RAG, local voice fallback, and record export continue.

Presenter line:

"The internet is gone, but the private LAN remains. That is the product promise: sensitive appointment inference stays in the room."

### If ElevenLabs On-Device Is Activated

Presenter line:

"The voice path is also local because official on-device access is active."

### If ElevenLabs On-Device Is Not Activated

Presenter line:

"ElevenLabs gives the sponsor-quality voice online. For the offline privacy proof, we deliberately switch to local ASR/TTS fallback. We would rather be honest about activation than overclaim privacy."

## Things Not To Do

- Do not secretly switch to scripted replay while calling it live recognition.
- Do not keep retrying a failing live sign in front of judges for more than 10 seconds.
- Do not explain a provider outage in detail; state the selected fallback and continue.
- Do not blame the signer, lighting, camera, or sponsor activation.
- Do not let low-confidence output become spoken English without confirmation.

