"""Check the local Signbridge orchestrator health endpoint."""

from __future__ import annotations

import json
import os
import sys
from urllib.request import urlopen


def main() -> int:
    base_url = os.getenv("SIGNBRIDGE_ORCHESTRATOR_URL", "http://127.0.0.1:8000").rstrip("/")
    with urlopen(f"{base_url}/health", timeout=5) as response:  # noqa: S310 - local dev helper.
        payload = json.loads(response.read().decode("utf-8"))

    print(json.dumps(payload, indent=2))
    return 0 if payload.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
