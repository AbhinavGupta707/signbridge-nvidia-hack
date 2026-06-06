"""Validate Signbridge event JSON files against the shared schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import ValidationError

from .signbridge_contracts import validate_event


def _load_events(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as events_file:
        payload = json.load(events_file)

    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return payload

    raise ValueError(f"{path} must contain one event object or an array of events")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 -m packages.contracts.validate <events.json> [...]", file=sys.stderr)
        return 2

    had_error = False
    for raw_path in sys.argv[1:]:
        path = Path(raw_path)
        try:
            events = _load_events(path)
            for index, event in enumerate(events):
                try:
                    validate_event(event)
                except ValidationError as exc:
                    had_error = True
                    print(f"{path}:{index}: INVALID: {exc.message}", file=sys.stderr)
            if not had_error:
                print(f"{path}: OK ({len(events)} event(s))")
        except Exception as exc:  # noqa: BLE001 - CLI should show a compact validation failure.
            had_error = True
            print(f"{path}: ERROR: {exc}", file=sys.stderr)

    return 1 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
