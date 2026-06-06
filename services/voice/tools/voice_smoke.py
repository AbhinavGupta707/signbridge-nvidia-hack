"""Smoke-test Signbridge voice providers against the shared event schema."""

from __future__ import annotations

import argparse
import base64
import json
from typing import Any

from packages.contracts import validate_events
from services.voice.signbridge_voice.config import VoiceConfig
from services.voice.signbridge_voice.providers import build_voice_providers


def build_smoke_events(config: VoiceConfig) -> list[dict[str, Any]]:
    providers = build_voice_providers(config)
    recognition = {
        "type": "recognition.final",
        "session_id": "demo-001",
        "utterance_id": "u-voice-smoke",
        "t_ms": 1000,
        "tokens": ["MY_HOME", "DAMP", "CHILD_ASTHMA"],
        "confidence": 0.84,
    }
    audio = {
        "type": "audio.chunk",
        "session_id": "demo-001",
        "t_ms": 1500,
        "format": "pcm16",
        "sample_rate": 16000,
        "data_b64": base64.b64encode(b"\x00\x00" * 1600).decode("ascii"),
    }
    events: list[dict[str, Any]] = []
    events.extend(providers.status_events())
    events.extend(providers.translate_and_speak(recognition))
    events.extend(providers.caption_chunk(audio))
    return validate_events(events)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print generated events as JSON.")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock ASR/TTS and template translation regardless of environment.",
    )
    args = parser.parse_args()

    config = VoiceConfig.from_env()
    if args.mock:
        config = VoiceConfig(
            llm_provider="mock",
            translation_mode="template",
            tts_provider="mock",
            asr_provider="mock",
        )

    events = build_smoke_events(config)
    if args.json:
        print(json.dumps(events, indent=2))
    else:
        print(f"voice smoke OK ({len(events)} contract-valid event(s))")
        print(json.dumps(config.summary(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

