"""FastAPI WebSocket orchestrator for mock and pre-hardware hybrid modes."""

from __future__ import annotations

import asyncio
import os
from typing import Any

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from jsonschema import ValidationError

from packages.contracts import EVENT_TYPES, SCHEMA_PATH, load_sample_events, validate_event
from services.orchestrator.providers import HybridProviders, MockProviders

SCENARIO = "housing_repair"


def _env_mode() -> str:
    return os.environ.get("SIGNBRIDGE_ORCHESTRATOR_MODE", "mock").strip().lower() or "mock"


class SignbridgeOrchestrator:
    def __init__(self, *, mode: str = "mock") -> None:
        self.mode = mode if mode in {"mock", "hybrid"} else "mock"
        self.providers = HybridProviders() if self.mode == "hybrid" else MockProviders()

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "signbridge-orchestrator",
            "mode": self.mode,
            "scenario": SCENARIO,
            "contracts": {
                "schema_path": str(SCHEMA_PATH),
                "event_types": list(EVENT_TYPES),
            },
            "components": self._component_statuses(),
        }

    def _component_statuses(self) -> list[dict[str, Any]]:
        base = [{"component": "orchestrator", "status": "ready", "detail": "FastAPI WebSocket event bus"}]
        if self.mode == "hybrid":
            return [*base, *[_component_from_status_event(event) for event in self.providers.status_events()]]
        return [
            *base,
            {"component": "recognition", "status": "mock_ready", "detail": "no real vision model"},
            {"component": "translation", "status": "mock_ready", "detail": "no real LLM"},
            {"component": "tts", "status": "mock_ready", "detail": "no real voice provider"},
            {"component": "captions", "status": "mock_ready", "detail": "no real ASR"},
            {"component": "policy", "status": "mock_ready", "detail": "no real advocacy RAG"},
            {"component": "question", "status": "mock_ready", "detail": "scripted prompts"},
            {"component": "record", "status": "mock_ready", "detail": "in-memory record only"},
        ]

    def status_events(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "system.status",
                "component": component["component"],
                "status": component["status"],
                "detail": component["detail"],
            }
            for component in self.health()["components"]
        ]

    def handle_event(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        event_type = event["type"]

        if event_type == "session.start":
            if self.mode == "hybrid":
                return [self.providers.record.start_session(event)]
            return [self.providers.record.start_session(event["session_id"])]

        if event_type == "landmark.frame":
            recognition_events = self.providers.recognition.recognise_frame(event)
            final_recognition = recognition_events[-1]
            if self.mode == "hybrid":
                voice_events = self.providers.voice.translate_and_speak(final_recognition)
                advocacy_events = self.providers.advocacy.events_for(voice_events[0])
                events = [*recognition_events, *voice_events, *advocacy_events]
                return [*events, self._record_updates(*events)]

            translation = self.providers.translation.translate(final_recognition)
            tts = self.providers.tts.synthesize(translation)
            policy = self.providers.policy.policy_for(translation)
            question = self.providers.question.question_for(translation)
            return [
                *recognition_events,
                translation,
                tts,
                policy,
                question,
                self._record_updates(translation, policy, question),
            ]

        if event_type == "audio.chunk":
            caption_events = (
                self.providers.voice.caption_chunk(event)
                if self.mode == "hybrid"
                else self.providers.captions.caption_chunk(event)
            )
            final_caption = caption_events[-1]
            if self.mode == "hybrid":
                advocacy_events = self.providers.advocacy.events_for(
                    final_caption,
                    card_limit=2,
                    question_limit=1,
                )
                events = [*caption_events, *advocacy_events]
                return [*events, self._record_updates(*events)]

            policy = self.providers.policy.policy_for(final_caption)
            question = self.providers.question.question_for(final_caption)
            return [*caption_events, policy, question, self._record_updates(final_caption, policy, question)]

        if event_type == "user.confirmation":
            return [self.providers.record.note_confirmation(event)]

        if event_type == "record.export":
            return [self.providers.record.export(event["session_id"], event["format"])]

        if event_type == "demo.replay":
            return []

        return [
            {
                "type": "system.status",
                "component": "orchestrator",
                "status": "ignored",
                "detail": f"No mock handler for {event_type}",
            }
        ]

    def _record_updates(self, *events: dict[str, Any]) -> dict[str, Any]:
        session_id = "demo-001"
        recordable = [
            event
            for event in events
            if event["type"] in {"translation.final", "caption.final", "policy.card", "question.prompt"}
        ]
        for event in recordable:
            if event.get("session_id"):
                session_id = event["session_id"]
        if hasattr(self.providers.record, "append_many"):
            self.providers.record.append_many(recordable)
        else:
            for event in recordable:
                self.providers.record.append(event)
        return self.providers.record.updated(session_id)


def _component_from_status_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "component": event["component"],
        "status": event["status"],
        "detail": event["detail"],
    }


def build_orchestrator(mode: str | None = None) -> SignbridgeOrchestrator:
    return SignbridgeOrchestrator(mode=mode or _env_mode())


orchestrator = build_orchestrator()
app = FastAPI(
    title="Signbridge Orchestrator",
    description="FastAPI orchestrator for mock replay and pre-hardware hybrid Signbridge integration.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, Any]:
    return orchestrator.health()


@app.get("/mock/events")
def mock_events() -> list[dict[str, Any]]:
    return load_sample_events()


@app.get("/mock/records/{session_id}.html")
def mock_record(session_id: str) -> HTMLResponse:
    return HTMLResponse(orchestrator.providers.record.render_html(session_id))


@app.get("/mock/records/{session_id}.json")
def mock_record_json(session_id: str) -> JSONResponse:
    return JSONResponse(orchestrator.providers.record.render_json(session_id))


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    replay: str | None = Query(default=None),
    delay_scale: float = Query(default=0.35, ge=0, le=2),
) -> None:
    await websocket.accept()
    await _send_events(websocket, orchestrator.status_events())

    if replay in {"1", "true", "scripted"}:
        await _stream_replay(websocket, delay_scale=delay_scale)

    try:
        while True:
            incoming = await websocket.receive_json()
            if not isinstance(incoming, dict):
                await _send_event(
                    websocket,
                    {
                        "type": "system.status",
                        "component": "orchestrator",
                        "status": "error",
                        "detail": "Incoming WebSocket payload must be a JSON object.",
                    },
                )
                continue

            try:
                validate_event(incoming)
            except ValidationError as exc:
                await _send_event(
                    websocket,
                    {
                        "type": "system.status",
                        "component": "orchestrator",
                        "status": "error",
                        "detail": f"Invalid event: {exc.message}",
                    },
                )
                continue

            if incoming["type"] == "demo.replay":
                await _stream_replay(websocket, delay_scale=delay_scale)
                continue

            await _send_events(websocket, orchestrator.handle_event(incoming))
    except WebSocketDisconnect:
        return


async def _stream_replay(websocket: WebSocket, delay_scale: float) -> None:
    previous_t_ms = 0
    for event in load_sample_events():
        t_ms = event.get("t_ms", previous_t_ms)
        wait_seconds = max(t_ms - previous_t_ms, 0) / 1000 * delay_scale
        previous_t_ms = t_ms
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)
        await _send_event(websocket, event)


async def _send_events(websocket: WebSocket, events: list[dict[str, Any]]) -> None:
    for event in events:
        await _send_event(websocket, event)


async def _send_event(websocket: WebSocket, event: dict[str, Any]) -> None:
    validate_event(event)
    await websocket.send_json(event)
