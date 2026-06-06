"""Smoke test a live hybrid WebSocket request/response flow."""

from __future__ import annotations

import asyncio
import json
import os

import websockets


async def _recv_until(websocket, predicate, *, timeout: float = 5.0) -> list[dict]:
    seen: list[dict] = []
    while True:
        raw_message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
        event = json.loads(raw_message)
        seen.append(event)
        if predicate(event, seen):
            return seen


async def _run() -> int:
    ws_url = os.getenv("SIGNBRIDGE_ORCHESTRATOR_WS", "ws://127.0.0.1:8000/ws")
    session_id = "ws-prehardware-001"
    all_events: list[dict] = []

    async with websockets.connect(ws_url) as websocket:
        all_events.extend(
            await _recv_until(
                websocket,
                lambda event, seen: len([item for item in seen if item["type"] == "system.status"]) >= 8,
            )
        )

        await websocket.send(
            json.dumps(
                {
                    "type": "session.start",
                    "session_id": session_id,
                    "scenario": "housing_repair_damp_mould",
                    "consent_record": True,
                }
            )
        )
        all_events.extend(await _recv_until(websocket, lambda event, _seen: event["type"] == "record.updated"))

        await websocket.send(
            json.dumps(
                {
                    "type": "landmark.frame",
                    "session_id": session_id,
                    "t_ms": 1000,
                    "landmarks_version": "mediapipe_holistic_v1",
                    "points": [],
                }
            )
        )
        all_events.extend(await _recv_until(websocket, lambda event, _seen: event["type"] == "record.updated"))

        await websocket.send(
            json.dumps(
                {
                    "type": "user.confirmation",
                    "session_id": session_id,
                    "utterance_id": "u-live-1",
                    "accepted": True,
                    "correction_text": None,
                }
            )
        )
        all_events.extend(await _recv_until(websocket, lambda event, _seen: event["type"] == "record.updated"))

        await websocket.send(
            json.dumps(
                {
                    "type": "audio.chunk",
                    "session_id": session_id,
                    "t_ms": 4000,
                    "format": "pcm16",
                    "sample_rate": 16000,
                    "data_b64": "U0lHTkJSSURHRV9NT0NLX0FVRElP",
                }
            )
        )
        all_events.extend(await _recv_until(websocket, lambda event, _seen: event["type"] == "record.updated"))

        await websocket.send(json.dumps({"type": "record.export", "session_id": session_id, "format": "html"}))
        all_events.extend(await _recv_until(websocket, lambda event, _seen: event["type"] == "record.exported"))

    policy_cards = [event for event in all_events if event["type"] == "policy.card"]
    source_backed = [
        card
        for card in policy_cards
        if card.get("citations") and not str(card.get("source_url", "")).startswith("mock:")
    ]
    if not source_backed:
        raise AssertionError("live WebSocket flow did not produce source-backed policy cards")

    print(
        "Hybrid WebSocket flow OK: "
        f"{len(all_events)} events; "
        f"{len(policy_cards)} policy cards; "
        f"{len(source_backed)} source-backed"
    )
    return 0


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
