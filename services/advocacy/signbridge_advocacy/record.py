from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import DEFAULT_EXAMPLES_DIR, DEFAULT_MANIFEST_PATH


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class RecordAgent:
    session_id: str
    scenario: str = "housing_repair_damp_mould"
    consent_record: bool = True
    manifest_path: Path = DEFAULT_MANIFEST_PATH
    started_at: str = field(default_factory=now_iso)
    utterances: list[dict[str, Any]] = field(default_factory=list)
    policy_cards: list[dict[str, Any]] = field(default_factory=list)
    question_prompts: list[dict[str, Any]] = field(default_factory=list)
    commitments: list[dict[str, Any]] = field(default_factory=list)

    def record_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type")
        if event_type in {"translation.final", "caption.final"}:
            self.utterances.append(
                {
                    "type": event_type,
                    "utterance_id": event.get("utterance_id"),
                    "speaker": event.get("speaker", "signer" if event_type == "translation.final" else "professional"),
                    "text": event.get("text", ""),
                    "confidence": event.get("confidence"),
                    "t_ms": event.get("t_ms"),
                }
            )
        elif event_type == "policy.card":
            self._assert_sourced_policy_card(event)
            self.policy_cards.append(event)
        elif event_type == "question.prompt":
            self.question_prompts.append(event)
        elif event_type == "commitment.recorded":
            self.commitments.append(event)

    def export_record(self) -> dict[str, Any]:
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return {
            "record_version": "signbridge.record.v1",
            "session_id": self.session_id,
            "scenario": self.scenario,
            "consent_record": self.consent_record,
            "started_at": self.started_at,
            "generated_at": now_iso(),
            "source_manifest": {
                "manifest_id": manifest["manifest_id"],
                "path": str(self.manifest_path),
                "last_verified": manifest["last_verified"],
            },
            "utterances": self.utterances,
            "policy_cards": self.policy_cards,
            "question_prompts": self.question_prompts,
            "commitments": self.commitments,
            "evidence_checklist": [
                "Photos or video stills showing location and extent of damp or mould, with dates.",
                "Date, time, channel, and reference number for each report.",
                "Household vulnerability details the resident consents to record, such as child, asthma, pregnancy, age, or mobility risk.",
                "Inspection appointment date, contractor name where provided, and written repair plan.",
                "Copies of complaint, written summary, repair updates, and any temporary accommodation decision.",
            ],
            "verified_notes": {
                "verified_for_demo": manifest.get("verified_for_demo", []),
                "needs_confirmation": manifest.get("needs_confirmation", []),
            },
            "safety_notes": manifest.get("safety_notes", []),
        }

    def export_event(self, *, export_url: str = "local://signbridge-record.json") -> dict[str, Any]:
        return {
            "type": "record.exported",
            "session_id": self.session_id,
            "format": "json",
            "export_url": export_url,
        }

    def export_html(self) -> str:
        record = self.export_record()
        cards = "\n".join(self._render_card(card) for card in record["policy_cards"])
        questions = "\n".join(
            f"<li>{html.escape(prompt['text'])}</li>" for prompt in record["question_prompts"]
        )
        utterances = "\n".join(
            f"<li><strong>{html.escape(item.get('speaker') or item['type'])}</strong>: {html.escape(item['text'])}</li>"
            for item in record["utterances"]
        )
        needs = "\n".join(
            f"<li>{html.escape(item)}</li>" for item in record["verified_notes"]["needs_confirmation"]
        )
        evidence = "\n".join(f"<li>{html.escape(item)}</li>" for item in record["evidence_checklist"])
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Signbridge Housing Repair Record</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 880px; margin: 32px auto; line-height: 1.5; color: #1d2733; }}
    h1, h2 {{ line-height: 1.2; }}
    article {{ border: 1px solid #d6dde6; border-radius: 8px; padding: 16px; margin: 12px 0; }}
    .claim {{ font-weight: 600; }}
    .source {{ color: #536070; font-size: 0.94rem; }}
  </style>
</head>
<body>
  <h1>Signbridge Housing Repair Record</h1>
  <p><strong>Session:</strong> {html.escape(record["session_id"])}<br>
  <strong>Scenario:</strong> {html.escape(record["scenario"])}<br>
  <strong>Generated:</strong> {html.escape(record["generated_at"])}</p>

  <h2>Transcript</h2>
  <ul>{utterances}</ul>

  <h2>Source-Backed Policy Cards</h2>
  {cards}

  <h2>Suggested Questions</h2>
  <ul>{questions}</ul>

  <h2>Evidence To Attach</h2>
  <ul>{evidence}</ul>

  <h2>Still Needs Confirmation</h2>
  <ul>{needs}</ul>
</body>
</html>
"""

    def write_exports(self, output_dir: Path = DEFAULT_EXAMPLES_DIR) -> tuple[Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        record_path = output_dir / "housing_repair_record.json"
        html_path = output_dir / "housing_repair_record.html"
        record_path.write_text(json.dumps(self.export_record(), indent=2) + "\n", encoding="utf-8")
        html_path.write_text(self.export_html(), encoding="utf-8")
        return record_path, html_path

    @staticmethod
    def _assert_sourced_policy_card(card: dict[str, Any]) -> None:
        missing = [key for key in ("claim", "source_title", "source_url", "quote") if not card.get(key)]
        citations = card.get("citations")
        if missing or not citations:
            raise ValueError(f"Policy card is missing required source fields: {missing or 'citations'}")
        for citation in citations:
            for key in ("source_title", "source_url", "quote"):
                if not citation.get(key):
                    raise ValueError(f"Policy card citation missing {key}: {card.get('id')}")

    @staticmethod
    def _render_card(card: dict[str, Any]) -> str:
        citations = "\n".join(
            "<li>"
            f"{html.escape(citation['source_title'])}: "
            f"<a href=\"{html.escape(citation['source_url'])}\">{html.escape(citation['locator'])}</a> "
            f"<span class=\"source\">quote: {html.escape(citation['quote'])}</span>"
            "</li>"
            for citation in card.get("citations", [])
        )
        return f"""<article>
  <h3>{html.escape(card["title"])}</h3>
  <p class="claim">{html.escape(card["claim"])}</p>
  <ul>{citations}</ul>
</article>"""
