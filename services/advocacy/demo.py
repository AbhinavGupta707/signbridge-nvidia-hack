#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from signbridge_advocacy import AdvocacyPipeline, RecordAgent
from signbridge_advocacy.paths import DEFAULT_EXAMPLES_DIR


def build_demo_events() -> tuple[list[dict], RecordAgent]:
    session_id = "demo-housing-001"
    transcript = (
        "There is damp and mould in my child's bedroom. My child has asthma and "
        "their breathing is getting worse. I am Deaf and need BSL or written updates."
    )
    professional_reply = (
        "I can arrange an inspection. Please send photos and I will log the vulnerability "
        "and repair request today."
    )

    events: list[dict] = [
        {
            "type": "session.start",
            "session_id": session_id,
            "scenario": "housing_repair_damp_mould",
            "consent_record": True,
        },
        {
            "type": "translation.final",
            "session_id": session_id,
            "utterance_id": "u-001",
            "text": transcript,
            "confidence": 0.86,
            "t_ms": 18400,
        },
        {
            "type": "caption.final",
            "session_id": session_id,
            "utterance_id": "c-001",
            "speaker": "professional",
            "text": professional_reply,
            "confidence": 0.91,
            "t_ms": 26100,
        },
    ]

    pipeline = AdvocacyPipeline()
    generated = pipeline.run_turn(
        " ".join([transcript, professional_reply]),
        session_id=session_id,
        utterance_id="u-001",
        card_limit=6,
        question_limit=5,
    )
    events.extend(generated["policy_cards"])
    events.extend(generated["question_prompts"])
    events.append(
        {
            "type": "record.updated",
            "session_id": session_id,
            "item_count": len(events),
        }
    )

    record_agent = RecordAgent(session_id=session_id, consent_record=True)
    for event in events:
        record_agent.record_event(event)
    events.append(record_agent.export_event(export_url="local://housing_repair_record.json"))
    return events, record_agent


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Signbridge advocacy demo events")
    parser.add_argument("--write-examples", action="store_true", help="Write JSON/HTML examples")
    args = parser.parse_args()

    events, record_agent = build_demo_events()
    if args.write_examples:
        DEFAULT_EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        events_path = DEFAULT_EXAMPLES_DIR / "housing_repair_demo_events.json"
        events_path.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
        record_path, html_path = record_agent.write_exports(DEFAULT_EXAMPLES_DIR)
        print(f"Wrote {events_path}")
        print(f"Wrote {record_path}")
        print(f"Wrote {html_path}")
    else:
        print(json.dumps(events, indent=2))


if __name__ == "__main__":
    main()
