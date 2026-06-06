"""Smoke test the `/ws` scripted replay path."""

from __future__ import annotations

import asyncio
import json
import os

import websockets


async def _run() -> int:
    ws_url = os.getenv("SIGNBRIDGE_ORCHESTRATOR_WS", "ws://127.0.0.1:8000/ws")
    seen: list[str] = []
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "type": "demo.replay",
                    "session_id": "demo-001",
                    "scenario": "housing_repair",
                }
            )
        )
        while True:
            raw_message = await asyncio.wait_for(websocket.recv(), timeout=5)
            event = json.loads(raw_message)
            seen.append(event["type"])
            if event["type"] == "record.exported":
                break

    print(f"WebSocket replay OK: {len(seen)} events; last={seen[-1]}")
    return 0


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
