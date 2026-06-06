"""Direct in-process smoke test for pre-hardware orchestrator wiring."""

from __future__ import annotations

from packages.contracts import validate_events
from services.orchestrator.app import build_orchestrator


def main() -> int:
    orchestrator = build_orchestrator(mode="hybrid")
    session_id = "prehardware-001"
    outbound: list[dict] = []

    client_events = [
        {
            "type": "session.start",
            "session_id": session_id,
            "scenario": "housing_repair_damp_mould",
            "consent_record": True,
        },
        {
            "type": "landmark.frame",
            "session_id": session_id,
            "t_ms": 1000,
            "landmarks_version": "mediapipe_holistic_v1",
            "points": [],
        },
        {
            "type": "user.confirmation",
            "session_id": session_id,
            "utterance_id": "u-live-1",
            "accepted": True,
            "correction_text": None,
        },
        {
            "type": "audio.chunk",
            "session_id": session_id,
            "t_ms": 4000,
            "format": "pcm16",
            "sample_rate": 16000,
            "data_b64": "U0lHTkJSSURHRV9NT0NLX0FVRElP",
        },
        {
            "type": "record.export",
            "session_id": session_id,
            "format": "html",
        },
    ]

    for event in client_events:
        outbound.extend(orchestrator.handle_event(event))

    validate_events(outbound)
    event_types = [event["type"] for event in outbound]
    policy_cards = [event for event in outbound if event["type"] == "policy.card"]
    source_backed = [
        card
        for card in policy_cards
        if card.get("citations") and not str(card.get("source_url", "")).startswith("mock:")
    ]

    if "translation.final" not in event_types:
        raise AssertionError("hybrid flow did not produce translation.final")
    if "tts.audio" not in event_types:
        raise AssertionError("hybrid flow did not produce tts.audio")
    if "caption.final" not in event_types:
        raise AssertionError("hybrid flow did not produce caption.final")
    if not source_backed:
        raise AssertionError("hybrid flow did not produce source-backed policy.card")
    if event_types[-1] != "record.exported":
        raise AssertionError(f"expected final event record.exported, got {event_types[-1]}")
    exported_record = orchestrator.providers.record.render_json(session_id)
    if not exported_record.get("confirmations"):
        raise AssertionError("hybrid JSON export did not include confirmation audit trail")

    print(
        "Hybrid direct flow OK: "
        f"{len(outbound)} events; "
        f"{len(policy_cards)} policy cards; "
        f"{len(source_backed)} source-backed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
