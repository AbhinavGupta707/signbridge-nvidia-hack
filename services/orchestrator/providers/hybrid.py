"""Hybrid local providers for pre-hardware Signbridge integration.

This mode keeps the hardware-dependent recognizer mocked, but routes the rest
of the event flow through local voice provider interfaces and source-backed
advocacy agents. It is the highest-fidelity path we can run before DGX/ZGX
hardware and consented sign clips are available.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from typing import Any

from packages.contracts import validate_event
from services.advocacy.signbridge_advocacy import AdvocacyPipeline, RecordAgent
from services.orchestrator.providers.mock import MockRecognitionProvider
from services.voice.signbridge_voice.config import VoiceConfig
from services.voice.signbridge_voice.providers import VoiceProviders, build_voice_providers


class HybridPolicyQuestionProvider:
    """Generate source-backed policy cards and questions from local advocacy."""

    def __init__(self) -> None:
        self.pipeline = AdvocacyPipeline()

    def events_for(
        self,
        event: dict[str, Any],
        *,
        card_limit: int = 3,
        question_limit: int = 2,
    ) -> list[dict[str, Any]]:
        text = str(event.get("text", "")).strip()
        if not text:
            return []

        generated = self.pipeline.run_turn(
            text,
            session_id=str(event.get("session_id") or "demo-001"),
            utterance_id=str(event.get("utterance_id") or f"{event['type']}-turn"),
            card_limit=card_limit,
            question_limit=question_limit,
        )
        return [
            validate_event(outbound)
            for outbound in [*generated["policy_cards"], *generated["question_prompts"]]
        ]


class HybridRecordProvider:
    """Consent-aware in-memory records backed by the advocacy RecordAgent."""

    def __init__(self) -> None:
        self._records: dict[str, RecordAgent] = {}
        self._confirmations: dict[str, list[dict[str, Any]]] = {}

    def start_session(self, event: dict[str, Any]) -> dict[str, Any]:
        session_id = event["session_id"]
        self._records[session_id] = RecordAgent(
            session_id=session_id,
            scenario=event.get("scenario", "housing_repair_damp_mould"),
            consent_record=bool(event.get("consent_record", True)),
        )
        self._confirmations[session_id] = []
        return self.updated(session_id)

    def append_many(self, events: list[dict[str, Any]]) -> None:
        for event in events:
            self.append(event)

    def append(self, event: dict[str, Any]) -> None:
        session_id = event.get("session_id")
        if not session_id:
            return
        record = self._records.setdefault(session_id, RecordAgent(session_id=session_id))
        record.record_event(event)

    def note_confirmation(self, event: dict[str, Any], session_id: str = "demo-001") -> dict[str, Any]:
        session_id = str(event.get("session_id") or session_id)
        self._confirmations.setdefault(session_id, []).append(event)
        return self.updated(session_id)

    def updated(self, session_id: str) -> dict[str, Any]:
        record = self._records.setdefault(session_id, RecordAgent(session_id=session_id))
        item_count = (
            len(record.utterances)
            + len(record.policy_cards)
            + len(record.question_prompts)
            + len(record.commitments)
            + len(self._confirmations.get(session_id, []))
        )
        return validate_event(
            {
                "type": "record.updated",
                "session_id": session_id,
                "item_count": item_count,
            }
        )

    def export(self, session_id: str, export_format: str) -> dict[str, Any]:
        self._records.setdefault(session_id, RecordAgent(session_id=session_id))
        suffix = "html" if export_format == "html" else "json"
        return validate_event(
            {
                "type": "record.exported",
                "session_id": session_id,
                "format": export_format,
                "export_url": f"/mock/records/{session_id}.{suffix}",
            }
        )

    def render_html(self, session_id: str) -> str:
        body = self._records.setdefault(session_id, RecordAgent(session_id=session_id)).export_html()
        confirmations = self._confirmations.get(session_id, [])
        if not confirmations:
            return body

        items = "\n".join(
            "<li>"
            f"{html.escape(item['utterance_id'])}: "
            f"{'accepted' if item['accepted'] else 'corrected'}"
            f"{' - ' + html.escape(item['correction_text']) if item.get('correction_text') else ''}"
            "</li>"
            for item in confirmations
        )
        audit_html = f"\n  <h2>Confirmation Audit</h2>\n  <ul>{items}</ul>\n"
        return body.replace("</body>", f"{audit_html}</body>")

    def render_json(self, session_id: str) -> dict[str, Any]:
        record = self._records.setdefault(session_id, RecordAgent(session_id=session_id)).export_record()
        record["confirmations"] = self._confirmations.get(session_id, [])
        return record


@dataclass
class HybridProviders:
    recognition: MockRecognitionProvider = field(default_factory=MockRecognitionProvider)
    voice_config: VoiceConfig = field(default_factory=VoiceConfig.from_env)
    advocacy: HybridPolicyQuestionProvider = field(default_factory=HybridPolicyQuestionProvider)
    record: HybridRecordProvider = field(default_factory=HybridRecordProvider)
    voice: VoiceProviders = field(init=False)

    def __post_init__(self) -> None:
        self.voice = build_voice_providers(self.voice_config)

    def status_events(self) -> list[dict[str, Any]]:
        return [
            validate_event(
                {
                    "type": "system.status",
                    "component": "recognition",
                    "status": "mock_ready",
                    "detail": "synthetic recognition until real clips/hardware are available",
                }
            ),
            *self.voice.status_events(),
            validate_event(
                {
                    "type": "system.status",
                    "component": "policy",
                    "status": "ready",
                    "detail": "local source-backed City of London housing retrieval",
                }
            ),
            validate_event(
                {
                    "type": "system.status",
                    "component": "question",
                    "status": "ready",
                    "detail": "local source-backed question prompts",
                }
            ),
            validate_event(
                {
                    "type": "system.status",
                    "component": "record",
                    "status": "ready",
                    "detail": "local citation-backed record export",
                }
            ),
        ]
