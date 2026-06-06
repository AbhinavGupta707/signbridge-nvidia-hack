const SESSION_ID = "demo-001";
const SCENARIO = "housing_repair";
const MOCK_AUDIO_B64 = "U0lHTkJSSURHRV9NT0NLX0FVRElP";
const MAX_HISTORY_ITEMS = 6;

const SCRIPTED_EVENTS = [
  {
    type: "system.status",
    t_ms: 0,
    component: "orchestrator",
    status: "fallback_ready",
    detail: "local browser replay, mock WebSocket unavailable",
  },
  {
    type: "system.status",
    t_ms: 0,
    component: "recognition",
    status: "mock_ready",
    detail: "scripted constrained-vocabulary recogniser",
  },
  {
    type: "system.status",
    t_ms: 0,
    component: "translation",
    status: "mock_ready",
    detail: "deterministic gloss-to-English templates",
  },
  {
    type: "system.status",
    t_ms: 0,
    component: "tts",
    status: "mock_ready",
    detail: "placeholder audio envelope, no voice provider",
  },
  {
    type: "system.status",
    t_ms: 0,
    component: "captions",
    status: "mock_ready",
    detail: "scripted professional captions",
  },
  {
    type: "system.status",
    t_ms: 0,
    component: "policy",
    status: "mock_ready",
    detail: "placeholder policy card, no RAG",
  },
  {
    type: "system.status",
    t_ms: 0,
    component: "question",
    status: "mock_ready",
    detail: "scripted question prompt",
  },
  {
    type: "system.status",
    t_ms: 0,
    component: "record",
    status: "mock_ready",
    detail: "browser-only record snapshot",
  },
  {
    type: "recognition.partial",
    session_id: SESSION_ID,
    utterance_id: "u-1",
    t_ms: 900,
    tokens: ["MY_HOME", "DAMP"],
    confidence: 0.76,
  },
  {
    type: "recognition.final",
    session_id: SESSION_ID,
    utterance_id: "u-1",
    t_ms: 1300,
    tokens: ["MY_HOME", "DAMP", "CHILD_ASTHMA"],
    confidence: 0.84,
  },
  {
    type: "translation.final",
    session_id: SESSION_ID,
    utterance_id: "u-1",
    t_ms: 1450,
    text: "There is damp in my home and it is affecting my child's asthma.",
    confidence: 0.84,
  },
  {
    type: "tts.audio",
    session_id: SESSION_ID,
    utterance_id: "u-1",
    t_ms: 1700,
    format: "wav",
    data_b64: MOCK_AUDIO_B64,
  },
  {
    type: "caption.partial",
    session_id: SESSION_ID,
    t_ms: 2400,
    speaker: "professional",
    text: "I can book an inspection for...",
  },
  {
    type: "caption.final",
    session_id: SESSION_ID,
    t_ms: 3100,
    speaker: "professional",
    text: "I can book an inspection for damp and mould and send the appointment details in writing.",
  },
  {
    type: "policy.card",
    session_id: SESSION_ID,
    t_ms: 3500,
    id: "p-1",
    title: "Housing repair next step",
    claim: "Mock policy card: ask for an inspection timescale and written confirmation for damp and mould concerns.",
    source_title: "Mock source placeholder - replace in advocacy branch",
    source_url: "mock://policy/housing-repair",
    quote: "Mock quote for wiring only. The advocacy branch must replace this with a source-backed citation.",
  },
  {
    type: "question.prompt",
    session_id: SESSION_ID,
    t_ms: 3800,
    id: "q-1",
    text: "Ask when the repair inspection will happen and how it will be confirmed in writing.",
  },
  {
    type: "record.updated",
    session_id: SESSION_ID,
    t_ms: 3900,
    item_count: 4,
  },
  {
    type: "recognition.partial",
    session_id: SESSION_ID,
    utterance_id: "u-2",
    t_ms: 4700,
    tokens: ["INTERPRETER", "APPOINTMENT"],
    confidence: 0.78,
  },
  {
    type: "recognition.final",
    session_id: SESSION_ID,
    utterance_id: "u-2",
    t_ms: 5100,
    tokens: ["INTERPRETER", "APPOINTMENT", "WRITING"],
    confidence: 0.86,
  },
  {
    type: "translation.final",
    session_id: SESSION_ID,
    utterance_id: "u-2",
    t_ms: 5250,
    text: "Please arrange a BSL interpreter for the next appointment and confirm it in writing.",
    confidence: 0.86,
  },
  {
    type: "tts.audio",
    session_id: SESSION_ID,
    utterance_id: "u-2",
    t_ms: 5500,
    format: "wav",
    data_b64: MOCK_AUDIO_B64,
  },
  {
    type: "policy.card",
    session_id: SESSION_ID,
    t_ms: 6100,
    id: "p-2",
    title: "Accessible communication",
    claim: "Mock policy card: record the request for accessible communication support and confirm the follow-up route.",
    source_title: "Mock source placeholder - replace in advocacy branch",
    source_url: "mock://policy/accessible-communication",
    quote: "Mock quote for wiring only. The advocacy branch must replace this with a source-backed citation.",
  },
  {
    type: "question.prompt",
    session_id: SESSION_ID,
    t_ms: 6350,
    id: "q-2",
    text: "Ask who is responsible for booking the interpreter and when you will receive confirmation.",
  },
  {
    type: "record.updated",
    session_id: SESSION_ID,
    t_ms: 6500,
    item_count: 8,
  },
];

const refs = {
  sessionId: document.querySelector("#session-id"),
  connectionPill: document.querySelector("#connection-pill"),
  offlinePill: document.querySelector("#offline-pill"),
  mediaMode: document.querySelector("#media-mode"),
  cameraPreview: document.querySelector("#camera-preview"),
  cameraPlaceholder: document.querySelector("#camera-placeholder"),
  cameraButton: document.querySelector("#camera-button"),
  micButton: document.querySelector("#mic-button"),
  cameraStateLabel: document.querySelector("#camera-state-label"),
  cameraStateDetail: document.querySelector("#camera-state-detail"),
  micStateLabel: document.querySelector("#mic-state-label"),
  micStateDetail: document.querySelector("#mic-state-detail"),
  startSessionButton: document.querySelector("#start-session-button"),
  replayButton: document.querySelector("#replay-button"),
  reconnectButton: document.querySelector("#reconnect-button"),
  recordConsentToggle: document.querySelector("#record-consent-toggle"),
  exportButton: document.querySelector("#export-button"),
  mockSignButton: document.querySelector("#mock-sign-button"),
  mockSpeechButton: document.querySelector("#mock-speech-button"),
  captionState: document.querySelector("#caption-state"),
  captionLive: document.querySelector("#caption-live"),
  captionHistory: document.querySelector("#caption-history"),
  recognitionState: document.querySelector("#recognition-state"),
  tokenRow: document.querySelector("#token-row"),
  confidenceBar: document.querySelector("#confidence-bar"),
  confidenceLabel: document.querySelector("#confidence-label"),
  translationCard: document.querySelector("#translation-card"),
  confirmationSummary: document.querySelector("#confirmation-summary"),
  confirmButton: document.querySelector("#confirm-button"),
  correctionButton: document.querySelector("#correction-button"),
  correctionPanel: document.querySelector("#correction-panel"),
  correctionText: document.querySelector("#correction-text"),
  sendCorrectionButton: document.querySelector("#send-correction-button"),
  spokenDot: document.querySelector("#spoken-dot"),
  spokenTitle: document.querySelector("#spoken-title"),
  spokenDetail: document.querySelector("#spoken-detail"),
  replaySpeechButton: document.querySelector("#replay-speech-button"),
  recordCount: document.querySelector("#record-count"),
  policyCount: document.querySelector("#policy-count"),
  policyList: document.querySelector("#policy-list"),
  questionCount: document.querySelector("#question-count"),
  questionList: document.querySelector("#question-list"),
  providerGrid: document.querySelector("#provider-grid"),
  exportLink: document.querySelector("#export-link"),
  agentStrip: document.querySelector("#agent-strip"),
  lastEvent: document.querySelector("#last-event"),
};

const state = {
  sessionId: SESSION_ID,
  ws: null,
  manuallyClosed: false,
  localTimers: [],
  localCounter: 2,
  connection: {
    status: "connecting",
    detail: "Mock WebSocket",
    tone: "pending",
  },
  permissions: {
    camera: {
      status: "not_requested",
      detail: "Landmark capture is waiting.",
      stream: null,
    },
    microphone: {
      status: "not_requested",
      detail: "Caption capture is waiting.",
      stream: null,
    },
  },
  providerStatuses: new Map(),
  latestRecognition: null,
  latestTranslation: null,
  pendingConfirmation: null,
  correctionOpen: false,
  confirmationByUtterance: new Map(),
  captions: [],
  captionPartial: "",
  policies: [],
  questions: [],
  recordCount: 0,
  recordEvents: [],
  exportUrl: null,
  spoken: {
    tone: "idle",
    title: "Spoken output waiting",
    detail: "A confirmed signed meaning will be spoken for the hearing professional.",
  },
  agents: makeInitialAgentState(),
  lastEventLabel: "No event received",
};

function makeInitialAgentState() {
  return [
    ["landmarks", "Landmarks", "Waiting", "Camera or clip feed", "idle"],
    ["recogniser", "Recogniser", "Waiting", "Constrained vocabulary", "idle"],
    ["fluency", "Fluency", "Waiting", "Gloss-to-English", "idle"],
    ["speech", "Speech", "Waiting", "Awaiting confirmation", "idle"],
    ["captions", "Captions", "Waiting", "Professional speech", "idle"],
    ["policy", "Policy", "Waiting", "Citation card", "idle"],
    ["question", "Question", "Waiting", "Follow-up prompt", "idle"],
    ["record", "Record", "Waiting", "Consent-controlled", "idle"],
  ].map(([key, label, status, detail, tone]) => ({
    key,
    label,
    status,
    detail,
    tone,
    updatedAt: null,
  }));
}

function init() {
  refs.sessionId.textContent = state.sessionId;
  bindEvents();
  renderAll();
  refreshPermissionHints();
  connectWebSocket();
}

function bindEvents() {
  refs.cameraButton.addEventListener("click", requestCamera);
  refs.micButton.addEventListener("click", requestMicrophone);
  refs.startSessionButton.addEventListener("click", startSession);
  refs.replayButton.addEventListener("click", replayDemo);
  refs.reconnectButton.addEventListener("click", reconnectWebSocket);
  refs.exportButton.addEventListener("click", exportRecord);
  refs.mockSignButton.addEventListener("click", sendMockSign);
  refs.mockSpeechButton.addEventListener("click", sendMockSpeech);
  refs.confirmButton.addEventListener("click", confirmMeaning);
  refs.correctionButton.addEventListener("click", openCorrection);
  refs.sendCorrectionButton.addEventListener("click", sendCorrection);
  refs.replaySpeechButton.addEventListener("click", () => {
    if (state.latestTranslation) {
      speakText(state.latestTranslation.text);
    }
  });

  refs.questionList.addEventListener("click", (event) => {
    const button = event.target.closest("[data-question-id]");
    if (!button) return;
    const prompt = state.questions.find((item) => item.id === button.dataset.questionId);
    if (!prompt) return;
    state.captionPartial = prompt.text;
    setAgent("question", "Queued", "Prompt selected for the appointment", "active");
    renderCaptions();
    renderAgents();
  });
}

async function refreshPermissionHints() {
  await Promise.all([queryPermission("camera"), queryPermission("microphone")]);
  renderPermissions();
}

async function queryPermission(kind) {
  if (!navigator.permissions || !navigator.permissions.query) return;

  try {
    const result = await navigator.permissions.query({ name: kind });
    if (result.state === "granted" && state.permissions[kind].status !== "granted") {
      state.permissions[kind].status = "available";
      state.permissions[kind].detail = "Permission can be enabled for this session.";
    }
    if (result.state === "denied") {
      state.permissions[kind].status = "blocked";
      state.permissions[kind].detail = "Browser permission is blocked.";
    }
    result.addEventListener("change", () => {
      state.permissions[kind].status = result.state === "denied" ? "blocked" : result.state;
      state.permissions[kind].detail =
        result.state === "denied"
          ? "Browser permission is blocked."
          : "Permission state changed in the browser.";
      renderPermissions();
    });
  } catch {
    state.permissions[kind].detail = "Browser permission API is unavailable.";
  }
}

async function requestCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    state.permissions.camera.status = "unavailable";
    state.permissions.camera.detail = "Camera API unavailable in this browser context.";
    renderPermissions();
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    stopStream(state.permissions.camera.stream);
    state.permissions.camera.stream = stream;
    state.permissions.camera.status = "granted";
    state.permissions.camera.detail = "Camera active for landmark capture.";
    refs.cameraPreview.srcObject = stream;
    await refs.cameraPreview.play();
    setAgent("landmarks", "Camera ready", "Media permission granted", "ready");
  } catch (error) {
    state.permissions.camera.status = "blocked";
    state.permissions.camera.detail = error.message || "Camera permission denied.";
    setAgent("landmarks", "Blocked", "Camera permission unavailable", "warning");
  }
  renderPermissions();
  renderAgents();
}

async function requestMicrophone() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    state.permissions.microphone.status = "unavailable";
    state.permissions.microphone.detail = "Microphone API unavailable in this browser context.";
    renderPermissions();
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    stopStream(state.permissions.microphone.stream);
    state.permissions.microphone.stream = stream;
    state.permissions.microphone.status = "granted";
    state.permissions.microphone.detail = "Microphone active for caption capture.";
    setAgent("captions", "Mic ready", "Media permission granted", "ready");
  } catch (error) {
    state.permissions.microphone.status = "blocked";
    state.permissions.microphone.detail = error.message || "Microphone permission denied.";
    setAgent("captions", "Blocked", "Microphone permission unavailable", "warning");
  }
  renderPermissions();
  renderAgents();
}

function stopStream(stream) {
  if (!stream) return;
  for (const track of stream.getTracks()) {
    track.stop();
  }
}

function connectWebSocket() {
  closeWebSocket();
  state.manuallyClosed = false;
  clearLocalReplay();
  setConnection("connecting", "Connecting to mock WebSocket", "pending");

  const wsUrl = getWebSocketUrl();
  let socket;
  try {
    socket = new WebSocket(wsUrl);
  } catch {
    startLocalReplay("Mock WebSocket URL is invalid.");
    return;
  }

  state.ws = socket;

  const fallbackTimer = window.setTimeout(() => {
    if (socket.readyState !== WebSocket.OPEN) {
      socket.close();
      startLocalReplay("Mock WebSocket did not open.");
    }
  }, 1800);

  socket.addEventListener("open", () => {
    window.clearTimeout(fallbackTimer);
    setConnection("connected", "Mock WebSocket connected", "ready");
    sendClientEvent({
      type: "session.start",
      session_id: state.sessionId,
      scenario: SCENARIO,
      consent_record: refs.recordConsentToggle.checked,
    });
  });

  socket.addEventListener("message", (message) => {
    try {
      const event = JSON.parse(message.data);
      handleServerEvent(event);
    } catch {
      setConnection("error", "Received malformed mock event", "error");
    }
  });

  socket.addEventListener("close", () => {
    window.clearTimeout(fallbackTimer);
    if (socket !== state.ws) return;
    if (!state.manuallyClosed && state.connection.status !== "fallback") {
      startLocalReplay("Mock WebSocket closed.");
    }
  });

  socket.addEventListener("error", () => {
    if (socket !== state.ws) return;
    setConnection("error", "Mock WebSocket error", "error");
  });

  renderAll();
}

function reconnectWebSocket() {
  resetConversation();
  connectWebSocket();
}

function closeWebSocket() {
  if (!state.ws) return;
  state.manuallyClosed = true;
  state.ws.close();
  state.ws = null;
}

function getWebSocketUrl() {
  const params = new URLSearchParams(window.location.search);
  const explicitUrl = params.get("ws");
  if (explicitUrl) return explicitUrl;
  return "ws://127.0.0.1:8000/ws?replay=scripted&delay_scale=0.35";
}

function startSession() {
  resetConversation();
  sendClientEvent({
    type: "session.start",
    session_id: state.sessionId,
    scenario: SCENARIO,
    consent_record: refs.recordConsentToggle.checked,
  });
  setAgent("record", "Session started", "Record consent captured", "active");
  renderAll();
}

function replayDemo() {
  resetConversation();
  sendClientEvent({
    type: "demo.replay",
    session_id: state.sessionId,
    scenario: SCENARIO,
  });
}

function sendMockSign() {
  sendClientEvent({
    type: "landmark.frame",
    session_id: state.sessionId,
    t_ms: Math.round(performance.now()),
    landmarks_version: "mediapipe_holistic_v1",
    points: [],
  });
}

function sendMockSpeech() {
  sendClientEvent({
    type: "audio.chunk",
    session_id: state.sessionId,
    t_ms: Math.round(performance.now()),
    format: "pcm16",
    sample_rate: 16000,
    data_b64: MOCK_AUDIO_B64,
  });
}

function exportRecord() {
  sendClientEvent({
    type: "record.export",
    session_id: state.sessionId,
    format: "html",
  });
}

function sendClientEvent(event) {
  if (state.ws && state.ws.readyState === WebSocket.OPEN) {
    state.ws.send(JSON.stringify(event));
    return;
  }

  if (event.type === "demo.replay") {
    startLocalReplay("Running local browser replay.");
    return;
  }

  for (const serverEvent of localResponseForClientEvent(event)) {
    handleServerEvent(serverEvent);
  }
}

function startLocalReplay(reason) {
  clearLocalReplay();
  setConnection("fallback", reason, "warning");

  let previousTime = 0;
  for (const event of SCRIPTED_EVENTS) {
    const eventTime = event.t_ms || previousTime;
    const wait = Math.max(eventTime - previousTime, 0) * 0.35;
    previousTime = eventTime;
    const timer = window.setTimeout(() => handleServerEvent({ ...event }), wait);
    state.localTimers.push(timer);
  }
}

function clearLocalReplay() {
  for (const timer of state.localTimers) {
    window.clearTimeout(timer);
  }
  state.localTimers = [];
}

function localResponseForClientEvent(event) {
  if (event.type === "session.start") {
    return [
      {
        type: "record.updated",
        session_id: event.session_id,
        item_count: 0,
      },
    ];
  }

  if (event.type === "landmark.frame") {
    state.localCounter += 1;
    const utteranceId = `u-local-${state.localCounter}`;
    return [
      {
        type: "recognition.partial",
        session_id: event.session_id,
        utterance_id: utteranceId,
        t_ms: event.t_ms + 80,
        tokens: ["REPAIR", "URGENT"],
        confidence: 0.75,
      },
      {
        type: "recognition.final",
        session_id: event.session_id,
        utterance_id: utteranceId,
        t_ms: event.t_ms + 180,
        tokens: ["REPAIR", "URGENT", "CHILD"],
        confidence: 0.82,
      },
      {
        type: "translation.final",
        session_id: event.session_id,
        utterance_id: utteranceId,
        t_ms: event.t_ms + 280,
        text: "The repair is urgent because a child is affected.",
        confidence: 0.82,
      },
      {
        type: "tts.audio",
        session_id: event.session_id,
        utterance_id: utteranceId,
        t_ms: event.t_ms + 360,
        format: "wav",
        data_b64: MOCK_AUDIO_B64,
      },
      {
        type: "policy.card",
        session_id: event.session_id,
        t_ms: event.t_ms + 460,
        id: "p-local-urgent-repair",
        title: "Urgent repair evidence",
        claim: "Mock policy card: record the health impact and ask for written inspection details.",
        source_title: "Mock source placeholder - replace in advocacy branch",
        source_url: "mock://policy/urgent-repair",
        quote: "Mock quote for wiring only. The advocacy branch must replace this with a source-backed citation.",
      },
      {
        type: "question.prompt",
        session_id: event.session_id,
        t_ms: event.t_ms + 520,
        id: "q-local-urgent-repair",
        text: "Ask what evidence is needed and whether the repair can be marked urgent.",
      },
      {
        type: "record.updated",
        session_id: event.session_id,
        t_ms: event.t_ms + 560,
        item_count: state.recordCount + 4,
      },
    ];
  }

  if (event.type === "audio.chunk") {
    return [
      {
        type: "caption.partial",
        session_id: event.session_id,
        t_ms: event.t_ms + 90,
        speaker: "professional",
        text: "I will add that to the repair report...",
      },
      {
        type: "caption.final",
        session_id: event.session_id,
        t_ms: event.t_ms + 240,
        speaker: "professional",
        text: "I will add that to the repair report and send the next appointment details in writing.",
      },
      {
        type: "record.updated",
        session_id: event.session_id,
        t_ms: event.t_ms + 300,
        item_count: state.recordCount + 1,
      },
    ];
  }

  if (event.type === "user.confirmation") {
    return [
      {
        type: "record.updated",
        session_id: state.sessionId,
        item_count: state.recordCount + 1,
      },
    ];
  }

  if (event.type === "record.export") {
    const exportUrl = buildLocalRecord();
    return [
      {
        type: "record.exported",
        session_id: event.session_id,
        format: event.format,
        export_url: exportUrl,
      },
    ];
  }

  return [];
}

function handleServerEvent(event) {
  if (!event || typeof event.type !== "string") return;

  if (event.session_id) state.sessionId = event.session_id;
  state.lastEventLabel = event.type;
  state.recordEvents.push(event);
  if (state.recordEvents.length > 80) {
    state.recordEvents = state.recordEvents.slice(-80);
  }

  switch (event.type) {
    case "system.status":
      state.providerStatuses.set(event.component, event);
      if (event.status.includes("fallback")) {
        refs.offlinePill.textContent = "Local fallback active";
        refs.offlinePill.className = "status-pill status-pill--warning";
      }
      break;
    case "recognition.partial":
      state.latestRecognition = event;
      setAgent("landmarks", "Receiving", "Mock landmark frame", "active");
      setAgent("recogniser", "Partial", event.tokens.join(" + "), "active");
      break;
    case "recognition.final":
      state.latestRecognition = event;
      setAgent("recogniser", "Final", `${asPercent(event.confidence)} confidence`, "ready");
      break;
    case "translation.final":
      state.latestTranslation = event;
      state.pendingConfirmation = event;
      state.correctionOpen = false;
      state.confirmationByUtterance.delete(event.utterance_id);
      setSpoken("pending", "Awaiting confirmation", "Confirm the signed meaning before speech output.");
      setAgent("fluency", "Ready", "English sentence prepared", "ready");
      break;
    case "tts.audio":
      setAgent("speech", "Prepared", `${event.format.toUpperCase()} envelope received`, "ready");
      if (state.pendingConfirmation) {
        setSpoken("pending", "Speech prepared", "TTS mock output is waiting for confirmation.");
      }
      break;
    case "caption.partial":
      state.captionPartial = event.text;
      setAgent("captions", "Partial", "Live ASR text streaming", "active");
      break;
    case "caption.final":
      state.captionPartial = "";
      state.captions.unshift(event);
      state.captions = state.captions.slice(0, MAX_HISTORY_ITEMS);
      setAgent("captions", "Final", "Caption committed", "ready");
      break;
    case "policy.card":
      upsertById(state.policies, event);
      setAgent("policy", "Ready", event.title, "ready");
      break;
    case "question.prompt":
      upsertById(state.questions, event);
      setAgent("question", "Ready", "Prompt surfaced", "ready");
      break;
    case "record.updated":
      state.recordCount = event.item_count;
      setAgent("record", "Updated", `${event.item_count} items`, "ready");
      break;
    case "record.exported":
      state.exportUrl = normalizeExportUrl(event.export_url);
      setAgent("record", "Exported", event.format.toUpperCase(), "ready");
      break;
    default:
      break;
  }

  renderAll();
}

function upsertById(list, item) {
  const existingIndex = list.findIndex((entry) => entry.id === item.id);
  if (existingIndex >= 0) {
    list.splice(existingIndex, 1);
  }
  list.unshift(item);
}

function confirmMeaning() {
  if (!state.pendingConfirmation) return;
  const event = state.pendingConfirmation;
  state.confirmationByUtterance.set(event.utterance_id, {
    accepted: true,
    correction_text: null,
  });
  state.pendingConfirmation = null;
  state.correctionOpen = false;
  sendClientEvent({
    type: "user.confirmation",
    utterance_id: event.utterance_id,
    accepted: true,
    correction_text: null,
  });
  speakText(event.text);
  renderAll();
}

function openCorrection() {
  if (!state.pendingConfirmation) return;
  state.correctionOpen = true;
  refs.correctionText.value = state.pendingConfirmation.text;
  renderConfirmation();
  refs.correctionText.focus();
}

function sendCorrection() {
  if (!state.pendingConfirmation) return;
  const event = state.pendingConfirmation;
  const correction = refs.correctionText.value.trim();
  state.confirmationByUtterance.set(event.utterance_id, {
    accepted: false,
    correction_text: correction || null,
  });
  state.pendingConfirmation = null;
  state.correctionOpen = false;
  sendClientEvent({
    type: "user.confirmation",
    utterance_id: event.utterance_id,
    accepted: false,
    correction_text: correction || null,
  });
  setSpoken("warning", "Correction recorded", "Speech output paused for the corrected meaning.");
  renderAll();
}

function speakText(text) {
  if (!("speechSynthesis" in window) || typeof SpeechSynthesisUtterance === "undefined") {
    setSpoken("warning", "Meaning confirmed", "Browser speech synthesis is unavailable.");
    renderSpoken();
    return;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.92;
  utterance.pitch = 1;
  utterance.onstart = () => {
    setSpoken("active", "Speaking now", text);
    setAgent("speech", "Speaking", "Browser speech synthesis", "active");
    renderSpoken();
    renderAgents();
  };
  utterance.onend = () => {
    setSpoken("ready", "Spoken output played", text);
    setAgent("speech", "Played", "Output complete", "ready");
    renderSpoken();
    renderAgents();
  };
  utterance.onerror = () => {
    setSpoken("warning", "Speech unavailable", "Browser speech synthesis could not play output.");
    setAgent("speech", "Unavailable", "Speech synthesis error", "warning");
    renderSpoken();
    renderAgents();
  };
  window.speechSynthesis.speak(utterance);
}

function setConnection(status, detail, tone) {
  state.connection = { status, detail, tone };
  renderConnection();
}

function setSpoken(tone, title, detail) {
  state.spoken = { tone, title, detail };
}

function setAgent(key, status, detail, tone) {
  const agent = state.agents.find((entry) => entry.key === key);
  if (!agent) return;
  agent.status = status;
  agent.detail = detail;
  agent.tone = tone;
  agent.updatedAt = Date.now();
}

function resetConversation() {
  clearLocalReplay();
  state.latestRecognition = null;
  state.latestTranslation = null;
  state.pendingConfirmation = null;
  state.correctionOpen = false;
  state.confirmationByUtterance.clear();
  state.captions = [];
  state.captionPartial = "";
  state.policies = [];
  state.questions = [];
  state.recordCount = 0;
  state.recordEvents = [];
  state.exportUrl = null;
  state.spoken = {
    tone: "idle",
    title: "Spoken output waiting",
    detail: "A confirmed signed meaning will be spoken for the hearing professional.",
  };
  state.agents = makeInitialAgentState();
  state.lastEventLabel = "No event received";
  renderAll();
}

function renderAll() {
  refs.sessionId.textContent = state.sessionId;
  renderConnection();
  renderPermissions();
  renderCaptions();
  renderRecognition();
  renderConfirmation();
  renderSpoken();
  renderPolicies();
  renderQuestions();
  renderProviders();
  renderRecord();
  renderAgents();
}

function renderConnection() {
  const toneClass = toneClassFor(state.connection.tone);
  refs.connectionPill.className = `status-pill ${toneClass}`;
  refs.connectionPill.textContent = sentenceCase(state.connection.status);

  if (state.connection.status === "connected") {
    refs.offlinePill.textContent = "Mock providers online";
    refs.offlinePill.className = "status-pill status-pill--ready";
  } else if (state.connection.status === "fallback") {
    refs.offlinePill.textContent = "Local fallback active";
    refs.offlinePill.className = "status-pill status-pill--warning";
  } else {
    refs.offlinePill.textContent = state.connection.detail;
    refs.offlinePill.className = `status-pill ${toneClass}`;
  }
}

function renderPermissions() {
  renderPermission("camera", refs.cameraStateLabel, refs.cameraStateDetail, refs.cameraButton);
  renderPermission("microphone", refs.micStateLabel, refs.micStateDetail, refs.micButton);

  const cameraGranted = state.permissions.camera.status === "granted";
  refs.cameraPreview.classList.toggle("is-active", cameraGranted);
  refs.cameraPlaceholder.hidden = cameraGranted;
  refs.mediaMode.textContent =
    cameraGranted || state.permissions.microphone.status === "granted" ? "Live media" : "Mock-ready";
}

function renderPermission(kind, label, detail, button) {
  const permission = state.permissions[kind];
  const displayName = kind === "microphone" ? "Microphone" : "Camera";
  label.textContent = `${displayName}: ${humanPermission(permission.status)}`;
  detail.textContent = permission.detail;
  button.disabled = permission.status === "granted";
  button.textContent = permission.status === "granted" ? `${displayName} active` : `Enable ${kind === "microphone" ? "mic" : "camera"}`;
}

function renderCaptions() {
  if (state.captionPartial) {
    refs.captionState.textContent = "Partial caption streaming";
    refs.captionLive.innerHTML = `<span>${escapeHtml(state.captionPartial)}</span>`;
  } else if (state.captions.length > 0) {
    refs.captionState.textContent = "Latest caption final";
    refs.captionLive.innerHTML = `<span>${escapeHtml(state.captions[0].text)}</span>`;
  } else {
    refs.captionState.textContent = "Waiting for professional speech";
    refs.captionLive.innerHTML = "<span>No live caption yet.</span>";
  }

  refs.captionHistory.innerHTML = state.captions
    .map(
      (caption) => `
        <li>
          <span>${escapeHtml(capitalise(caption.speaker))}</span>
          <p>${escapeHtml(caption.text)}</p>
        </li>
      `,
    )
    .join("");
}

function renderRecognition() {
  const recognition = state.latestRecognition;
  if (!recognition) {
    refs.recognitionState.textContent = "Waiting for signed phrase";
    refs.tokenRow.innerHTML = '<span class="empty-state">No tokens yet</span>';
    refs.confidenceBar.style.width = "0%";
    refs.confidenceLabel.textContent = "0%";
    refs.translationCard.innerHTML = '<span class="empty-state">No signed meaning recognised yet.</span>';
    return;
  }

  refs.recognitionState.textContent =
    recognition.type === "recognition.final" ? "Signed phrase final" : "Signed phrase partial";
  refs.tokenRow.innerHTML = recognition.tokens
    .map((token) => `<span class="token">${escapeHtml(token)}</span>`)
    .join("");
  refs.confidenceBar.style.width = `${Math.round(recognition.confidence * 100)}%`;
  refs.confidenceLabel.textContent = asPercent(recognition.confidence);

  if (state.latestTranslation) {
    refs.translationCard.innerHTML = `
      <span class="field-label">English output candidate</span>
      <p>${escapeHtml(state.latestTranslation.text)}</p>
      <span class="confidence-note">${escapeHtml(asPercent(state.latestTranslation.confidence))} translation confidence</span>
    `;
  }
}

function renderConfirmation() {
  const pending = state.pendingConfirmation;
  refs.correctionPanel.hidden = !state.correctionOpen;

  if (!pending) {
    const latest = state.latestTranslation;
    if (latest && state.confirmationByUtterance.has(latest.utterance_id)) {
      const confirmation = state.confirmationByUtterance.get(latest.utterance_id);
      refs.confirmationSummary.textContent = confirmation.accepted
        ? "Meaning confirmed for spoken output and record."
        : "Correction recorded for the appointment record.";
    } else {
      refs.confirmationSummary.textContent = "Waiting for a recognised signed meaning.";
    }
    refs.confirmButton.disabled = true;
    refs.correctionButton.disabled = true;
    return;
  }

  refs.confirmationSummary.textContent = `Check: "${pending.text}"`;
  refs.confirmButton.disabled = false;
  refs.correctionButton.disabled = false;
}

function renderSpoken() {
  refs.spokenDot.className = `status-dot status-dot--${state.spoken.tone}`;
  refs.spokenTitle.textContent = state.spoken.title;
  refs.spokenDetail.textContent = state.spoken.detail;
  refs.replaySpeechButton.disabled = !state.latestTranslation;
}

function renderPolicies() {
  refs.policyCount.textContent = `${state.policies.length} ${state.policies.length === 1 ? "card" : "cards"}`;
  if (state.policies.length === 0) {
    refs.policyList.innerHTML = '<p class="empty-state">No policy card surfaced yet.</p>';
    return;
  }

  refs.policyList.innerHTML = state.policies
    .map((policy) => {
      const source = sourceMarkup(policy);
      return `
        <article class="policy-card">
          <h3>${escapeHtml(policy.title)}</h3>
          <p>${escapeHtml(policy.claim)}</p>
          <blockquote>${escapeHtml(policy.quote)}</blockquote>
          ${source}
        </article>
      `;
    })
    .join("");
}

function renderQuestions() {
  refs.questionCount.textContent = `${state.questions.length} ${state.questions.length === 1 ? "prompt" : "prompts"}`;
  if (state.questions.length === 0) {
    refs.questionList.innerHTML = '<p class="empty-state">No prompt yet.</p>';
    return;
  }

  refs.questionList.innerHTML = state.questions
    .map(
      (question) => `
        <article class="question-card">
          <p>${escapeHtml(question.text)}</p>
          <button class="button button--small" type="button" data-question-id="${escapeHtml(question.id)}">
            Queue prompt
          </button>
        </article>
      `,
    )
    .join("");
}

function renderProviders() {
  const components = [
    "orchestrator",
    "recognition",
    "translation",
    "tts",
    "captions",
    "policy",
    "question",
    "record",
  ];

  refs.providerGrid.innerHTML = components
    .map((component) => {
      const status = state.providerStatuses.get(component);
      const tone = providerTone(status?.status);
      return `
        <div class="provider-row">
          <span class="status-dot status-dot--${tone}"></span>
          <div>
            <strong>${escapeHtml(capitalise(component))}</strong>
            <span>${escapeHtml(status?.status || "waiting")}</span>
          </div>
        </div>
      `;
    })
    .join("");

  if (state.exportUrl) {
    refs.exportLink.innerHTML = `<a class="button button--link" href="${escapeHtml(state.exportUrl)}" target="_blank" rel="noreferrer">Open exported record</a>`;
  } else {
    refs.exportLink.innerHTML = "";
  }
}

function renderRecord() {
  refs.recordCount.textContent = `${state.recordCount} ${state.recordCount === 1 ? "record item" : "record items"}`;
}

function renderAgents() {
  refs.lastEvent.textContent = state.lastEventLabel;
  refs.agentStrip.innerHTML = state.agents
    .map(
      (agent) => `
        <div class="agent-step agent-step--${agent.tone}">
          <span>${escapeHtml(agent.label)}</span>
          <strong>${escapeHtml(agent.status)}</strong>
          <small>${escapeHtml(agent.detail)}</small>
        </div>
      `,
    )
    .join("");
}

function sourceMarkup(policy) {
  if (/^https?:\/\//.test(policy.source_url)) {
    return `<a href="${escapeHtml(policy.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(policy.source_title)}</a>`;
  }
  return `<span class="source-text">${escapeHtml(policy.source_title)}</span>`;
}

function normalizeExportUrl(exportUrl) {
  if (exportUrl.startsWith("blob:")) return exportUrl;
  if (/^https?:\/\//.test(exportUrl)) return exportUrl;
  try {
    const wsUrl = new URL(getWebSocketUrl());
    const protocol = wsUrl.protocol === "wss:" ? "https:" : "http:";
    return `${protocol}//${wsUrl.host}${exportUrl}`;
  } catch {
    return exportUrl;
  }
}

function buildLocalRecord() {
  const rows = state.recordEvents
    .filter((event) =>
      ["translation.final", "caption.final", "policy.card", "question.prompt"].includes(event.type),
    )
    .map((event) => {
      const body = event.text || event.claim || event.title || event.id || "";
      return `<li><strong>${escapeHtml(event.type)}</strong>: ${escapeHtml(body)}</li>`;
    })
    .join("");

  const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Signbridge Demo Record</title>
    <style>
      body { font-family: system-ui, sans-serif; max-width: 760px; margin: 40px auto; line-height: 1.5; color: #17202a; }
      h1 { font-size: 28px; }
      li { margin: 12px 0; }
    </style>
  </head>
  <body>
    <h1>Signbridge Demo Record: ${escapeHtml(state.sessionId)}</h1>
    <p>Constrained public-service vocabulary demo. Not certified interpretation.</p>
    <ol>${rows}</ol>
  </body>
</html>`;

  const blob = new Blob([html], { type: "text/html" });
  return URL.createObjectURL(blob);
}

function providerTone(status = "") {
  if (status.includes("ready") || status === "ok") return "ready";
  if (status.includes("error") || status.includes("blocked")) return "error";
  if (status.includes("fallback") || status.includes("mock")) return "warning";
  return "idle";
}

function toneClassFor(tone) {
  if (tone === "ready") return "status-pill--ready";
  if (tone === "warning") return "status-pill--warning";
  if (tone === "error") return "status-pill--error";
  return "";
}

function humanPermission(status) {
  return status.replace(/_/g, " ");
}

function sentenceCase(value) {
  const text = String(value || "").replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function capitalise(value) {
  const text = String(value || "");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function asPercent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return entities[char];
  });
}

init();
