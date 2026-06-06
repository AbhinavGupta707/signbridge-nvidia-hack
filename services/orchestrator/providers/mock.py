"""Mock provider layer for the initial Signbridge integration scaffold."""

from __future__ import annotations

import html
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

MOCK_AUDIO_B64 = "U0lHTkJSSURHRV9NT0NLX0FVRElP"


class MockRecognitionProvider:
    """Deterministic placeholder for the future constrained sign recogniser."""

    def __init__(self) -> None:
        self._counter = 0

    def recognise_frame(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        self._counter += 1
        utterance_id = f"u-live-{self._counter}"
        session_id = event["session_id"]
        t_ms = event["t_ms"]

        return [
            {
                "type": "recognition.partial",
                "session_id": session_id,
                "utterance_id": utterance_id,
                "t_ms": t_ms + 80,
                "tokens": ["MY_HOME", "DAMP"],
                "confidence": 0.74,
            },
            {
                "type": "recognition.final",
                "session_id": session_id,
                "utterance_id": utterance_id,
                "t_ms": t_ms + 180,
                "tokens": ["MY_HOME", "DAMP", "CHILD_ASTHMA"],
                "confidence": 0.84,
            },
        ]


class MockTranslationProvider:
    """Deterministic gloss-to-English templates. No LLM call is made."""

    _templates = {
        ("MY_HOME", "DAMP", "CHILD_ASTHMA"): "There is damp in my home and it is affecting my child's asthma.",
        ("INTERPRETER", "APPOINTMENT", "WRITING"): "Please arrange a BSL interpreter for the next appointment and confirm it in writing.",
        ("REPAIR", "URGENT", "CHILD"): "The repair is urgent because a child is affected.",
    }

    def translate(self, recognition_event: dict[str, Any]) -> dict[str, Any]:
        tokens = tuple(recognition_event["tokens"])
        text = self._templates.get(tokens, " ".join(tokens).replace("_", " ").capitalize() + ".")

        return {
            "type": "translation.final",
            "session_id": recognition_event.get("session_id"),
            "utterance_id": recognition_event["utterance_id"],
            "t_ms": recognition_event.get("t_ms", 0) + 100,
            "text": text,
            "confidence": recognition_event["confidence"],
        }


class MockTtsProvider:
    """Placeholder TTS provider. It returns a mock audio envelope only."""

    def synthesize(self, translation_event: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "tts.audio",
            "session_id": translation_event.get("session_id"),
            "utterance_id": translation_event["utterance_id"],
            "t_ms": translation_event.get("t_ms", 0) + 120,
            "format": "wav",
            "data_b64": MOCK_AUDIO_B64,
        }


class MockCaptionProvider:
    """Scripted reverse-path captions for professional speech."""

    def caption_chunk(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        session_id = event["session_id"]
        t_ms = event["t_ms"]
        return [
            {
                "type": "caption.partial",
                "session_id": session_id,
                "t_ms": t_ms + 90,
                "speaker": "professional",
                "text": "I can book an inspection for...",
            },
            {
                "type": "caption.final",
                "session_id": session_id,
                "t_ms": t_ms + 240,
                "speaker": "professional",
                "text": "I can book an inspection for damp and mould and send the appointment details in writing.",
            },
        ]


class MockPolicyCardProvider:
    """Placeholder policy-card provider. It does not perform retrieval."""

    def policy_for(self, event: dict[str, Any]) -> dict[str, Any]:
        text = event.get("text", "")
        if "interpreter" in text.lower():
            return {
                "type": "policy.card",
                "session_id": event.get("session_id"),
                "t_ms": event.get("t_ms", 0) + 160,
                "id": "p-accessible-communication",
                "title": "Accessible communication",
                "claim": "Mock policy card: record the request for accessible communication support and confirm the follow-up route.",
                "source_title": "Mock source placeholder - replace in advocacy branch",
                "source_url": "mock://policy/accessible-communication",
                "quote": "Mock quote for wiring only. The advocacy branch must replace this with a source-backed citation.",
            }

        return {
            "type": "policy.card",
            "session_id": event.get("session_id"),
            "t_ms": event.get("t_ms", 0) + 160,
            "id": "p-housing-repair",
            "title": "Housing repair next step",
            "claim": "Mock policy card: ask for an inspection timescale and written confirmation for damp and mould concerns.",
            "source_title": "Mock source placeholder - replace in advocacy branch",
            "source_url": "mock://policy/housing-repair",
            "quote": "Mock quote for wiring only. The advocacy branch must replace this with a source-backed citation.",
        }


class MockQuestionPromptProvider:
    """Scripted question prompt provider."""

    def question_for(self, event: dict[str, Any]) -> dict[str, Any]:
        text = event.get("text", "")
        if "interpreter" in text.lower():
            question = "Ask who is responsible for booking the interpreter and when you will receive confirmation."
            question_id = "q-accessible-communication"
        else:
            question = "Ask when the repair inspection will happen and how it will be confirmed in writing."
            question_id = "q-housing-repair"

        return {
            "type": "question.prompt",
            "session_id": event.get("session_id"),
            "t_ms": event.get("t_ms", 0) + 220,
            "id": question_id,
            "text": question,
        }


class MockRecordProvider:
    """In-memory appointment record for local demo wiring."""

    def __init__(self) -> None:
        self._items: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def start_session(self, session_id: str) -> dict[str, Any]:
        self._items[session_id] = []
        return self.updated(session_id)

    def append(self, event: dict[str, Any]) -> None:
        session_id = event.get("session_id")
        if not session_id:
            return
        if event["type"] in {
            "translation.final",
            "caption.final",
            "policy.card",
            "question.prompt",
            "record.exported",
        }:
            self._items[session_id].append(event)

    def note_confirmation(self, event: dict[str, Any], session_id: str = "demo-001") -> dict[str, Any]:
        session_id = str(event.get("session_id") or session_id)
        self._items[session_id].append(
            {
                "type": "user.confirmation",
                "session_id": session_id,
                "utterance_id": event["utterance_id"],
                "accepted": event["accepted"],
                "correction_text": event["correction_text"],
            }
        )
        return self.updated(session_id)

    def updated(self, session_id: str, t_ms: int | None = None) -> dict[str, Any]:
        event: dict[str, Any] = {
            "type": "record.updated",
            "session_id": session_id,
            "item_count": len(self._items[session_id]),
        }
        if t_ms is not None:
            event["t_ms"] = t_ms
        return event

    def export(self, session_id: str, export_format: str) -> dict[str, Any]:
        export_event = {
            "type": "record.exported",
            "session_id": session_id,
            "format": export_format,
            "export_url": f"/mock/records/{session_id}.html",
        }
        self.append(export_event)
        return export_event

    def render_html(self, session_id: str) -> str:
        items = self._items.get(session_id, [])
        rows = []
        for item in items:
            rows.append(
                "<li>"
                f"<strong>{html.escape(item['type'])}</strong>: "
                f"{html.escape(item.get('text') or item.get('claim') or item.get('title') or item.get('id') or '')}"
                "</li>"
            )

        return (
            "<!doctype html>"
            "<html><head><meta charset=\"utf-8\"><title>Signbridge Mock Record</title>"
            "<style>body{font-family:system-ui,sans-serif;max-width:760px;margin:40px auto;line-height:1.5;}"
            "h1{font-size:28px;}li{margin:12px 0;}</style></head>"
            "<body>"
            f"<h1>Signbridge Mock Record: {html.escape(session_id)}</h1>"
            "<p>This is a mock integration record. Real advocacy, consent, and export logic belongs to feature branches.</p>"
            f"<ol>{''.join(rows)}</ol>"
            "</body></html>"
        )

    def render_json(self, session_id: str) -> dict[str, Any]:
        return {
            "record_version": "signbridge.mock_record.v1",
            "session_id": session_id,
            "items": self._items.get(session_id, []),
        }


@dataclass
class MockProviders:
    recognition: MockRecognitionProvider = field(default_factory=MockRecognitionProvider)
    translation: MockTranslationProvider = field(default_factory=MockTranslationProvider)
    tts: MockTtsProvider = field(default_factory=MockTtsProvider)
    captions: MockCaptionProvider = field(default_factory=MockCaptionProvider)
    policy: MockPolicyCardProvider = field(default_factory=MockPolicyCardProvider)
    question: MockQuestionPromptProvider = field(default_factory=MockQuestionPromptProvider)
    record: MockRecordProvider = field(default_factory=MockRecordProvider)
