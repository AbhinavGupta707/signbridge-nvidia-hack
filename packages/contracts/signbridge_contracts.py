"""Runtime helpers for the shared Signbridge event contract."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

CONTRACT_ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = CONTRACT_ROOT / "events.schema.json"
EXAMPLES_ROOT = CONTRACT_ROOT / "examples"

EVENT_TYPES = (
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
)


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        return json.load(schema_file)


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    return Draft202012Validator(load_schema())


def validate_event(event: dict[str, Any]) -> dict[str, Any]:
    """Validate one event and return it unchanged for easy pipeline use."""

    _validator().validate(event)
    return event


def validate_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for event in events:
        validate_event(event)
    return events


def load_sample_events(filename: str = "scripted_demo.server.events.json") -> list[dict[str, Any]]:
    sample_path = EXAMPLES_ROOT / filename
    with sample_path.open("r", encoding="utf-8") as sample_file:
        events = json.load(sample_file)

    if not isinstance(events, list):
        raise ValueError(f"Expected a JSON array in {sample_path}")

    return validate_events(events)
