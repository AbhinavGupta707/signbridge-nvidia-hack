export const EVENT_TYPES = [
  "session.start",
  "landmark.frame",
  "audio.chunk",
  "user.confirmation",
  "record.export",
  "system.status",
  "recognition.partial",
  "recognition.final",
  "translation.final",
  "tts.audio",
  "caption.partial",
  "caption.final",
  "policy.card",
  "question.prompt",
  "record.updated",
  "record.exported",
  "demo.replay",
] as const;

export type EventType = (typeof EVENT_TYPES)[number];

export interface BaseEvent {
  type: EventType;
  session_id?: string;
  utterance_id?: string;
  t_ms?: number;
}

export interface SessionStartEvent extends BaseEvent {
  type: "session.start";
  session_id: string;
  scenario: string;
  consent_record: boolean;
}

export interface LandmarkFrameEvent extends BaseEvent {
  type: "landmark.frame";
  session_id: string;
  t_ms: number;
  landmarks_version: string;
  points: unknown[];
}

export interface AudioChunkEvent extends BaseEvent {
  type: "audio.chunk";
  session_id: string;
  t_ms: number;
  format: string;
  sample_rate: number;
  data_b64: string;
}

export interface UserConfirmationEvent extends BaseEvent {
  type: "user.confirmation";
  session_id: string;
  utterance_id: string;
  accepted: boolean;
  correction_text: string | null;
}

export interface RecordExportEvent extends BaseEvent {
  type: "record.export";
  session_id: string;
  format: string;
}

export interface SystemStatusEvent extends BaseEvent {
  type: "system.status";
  component: string;
  status: string;
  detail: string | null;
}

export interface RecognitionEvent extends BaseEvent {
  type: "recognition.partial" | "recognition.final";
  utterance_id: string;
  tokens: string[];
  confidence: number;
}

export interface TranslationFinalEvent extends BaseEvent {
  type: "translation.final";
  utterance_id: string;
  text: string;
  confidence: number;
}

export interface TtsAudioEvent extends BaseEvent {
  type: "tts.audio";
  utterance_id: string;
  format: string;
  data_b64: string;
}

export interface CaptionEvent extends BaseEvent {
  type: "caption.partial" | "caption.final";
  speaker: string;
  text: string;
  confidence?: number;
}

export interface Citation {
  source_id?: string;
  source_title: string;
  publisher?: string;
  source_url: string;
  quote: string;
  locator?: string;
  verified?: boolean;
  verified_on?: string;
}

export interface PolicyCardEvent extends BaseEvent {
  type: "policy.card";
  id: string;
  title: string;
  claim: string;
  source_title: string;
  source_url: string;
  quote: string;
  citations?: Citation[];
  policy_domain?: string;
  verified?: boolean;
}

export interface QuestionPromptEvent extends BaseEvent {
  type: "question.prompt";
  id: string;
  text: string;
  policy_card_ids?: string[];
  citations?: Citation[];
}

export interface RecordUpdatedEvent extends BaseEvent {
  type: "record.updated";
  session_id: string;
  item_count: number;
}

export interface RecordExportedEvent extends BaseEvent {
  type: "record.exported";
  session_id: string;
  format: string;
  export_url: string;
}

export interface DemoReplayEvent extends BaseEvent {
  type: "demo.replay";
  session_id?: string;
  scenario?: string;
}

export type ClientEvent =
  | SessionStartEvent
  | LandmarkFrameEvent
  | AudioChunkEvent
  | UserConfirmationEvent
  | RecordExportEvent
  | DemoReplayEvent;

export type ServerEvent =
  | SystemStatusEvent
  | RecognitionEvent
  | TranslationFinalEvent
  | TtsAudioEvent
  | CaptionEvent
  | PolicyCardEvent
  | QuestionPromptEvent
  | RecordUpdatedEvent
  | RecordExportedEvent;

export type SignbridgeEvent = ClientEvent | ServerEvent;
