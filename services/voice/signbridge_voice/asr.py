"""ASR provider interfaces and local fallback implementations."""

from __future__ import annotations

import base64
import re
import shutil
import subprocess
import tempfile
import wave
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Protocol

from packages.contracts import validate_event

from .config import VoiceConfig

DEFAULT_PROFESSIONAL_REPLY = (
    "I can book an inspection for damp and mould and send the appointment details in writing."
)


class ASRProvider(Protocol):
    name: str

    def status(self) -> dict[str, Any]:
        """Return a system.status event."""

    def caption_chunk(self, audio_event: dict[str, Any]) -> list[dict[str, Any]]:
        """Return caption.partial and caption.final events."""


def _status(component: str, status: str, detail: str) -> dict[str, Any]:
    return validate_event(
        {
            "type": "system.status",
            "component": component,
            "status": status,
            "detail": detail,
        }
    )


def _caption_event(
    audio_event: dict[str, Any],
    *,
    event_type: str,
    text: str,
    latency_ms: int,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "type": event_type,
        "speaker": "professional",
        "text": text,
    }
    if audio_event.get("session_id"):
        event["session_id"] = audio_event["session_id"]
    t_ms = audio_event.get("t_ms")
    if isinstance(t_ms, int):
        event["t_ms"] = t_ms + latency_ms
    return validate_event(event)


class MockASRProvider:
    """Scripted captions for orchestrator-compatible integration tests."""

    name = "mock_asr"

    def status(self) -> dict[str, Any]:
        return _status("captions", "mock_ready", "scripted caption events; not live ASR")

    def caption_chunk(self, audio_event: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            _caption_event(
                audio_event,
                event_type="caption.partial",
                text="I can book an inspection for...",
                latency_ms=90,
            ),
            _caption_event(
                audio_event,
                event_type="caption.final",
                text=DEFAULT_PROFESSIONAL_REPLY,
                latency_ms=240,
            ),
        ]


class TypedASRProvider:
    """Clearly labelled operator-typed reverse-path fallback."""

    name = "typed_asr"

    def __init__(self, caption_text: str = "") -> None:
        self.caption_text = caption_text or DEFAULT_PROFESSIONAL_REPLY

    def status(self) -> dict[str, Any]:
        return _status("captions", "fallback_ready", "typed/canned professional caption fallback")

    def caption_chunk(self, audio_event: dict[str, Any]) -> list[dict[str, Any]]:
        words = self.caption_text.split()
        partial = " ".join(words[: min(6, len(words))])
        if len(words) > 6:
            partial += "..."
        return [
            _caption_event(audio_event, event_type="caption.partial", text=partial, latency_ms=80),
            _caption_event(audio_event, event_type="caption.final", text=self.caption_text, latency_ms=180),
        ]


class LocalWhisperASRProvider:
    """Offline ASR using whisper.cpp when installed and model-cached."""

    name = "local_whisper_asr"

    def __init__(self, config: VoiceConfig, fallback: ASRProvider | None = None) -> None:
        self.config = config
        self.fallback = fallback or TypedASRProvider(config.typed_caption_text)

    def status(self) -> dict[str, Any]:
        if self._ready():
            return _status("captions", "ready", "local whisper.cpp ASR")
        return _status("captions", "fallback_ready", "whisper.cpp unavailable; typed/canned captions")

    def caption_chunk(self, audio_event: dict[str, Any]) -> list[dict[str, Any]]:
        if not self._ready():
            return self.fallback.caption_chunk(audio_event)
        try:
            text = self._transcribe(audio_event)
        except (OSError, ValueError, subprocess.SubprocessError):
            return self.fallback.caption_chunk(audio_event)
        if not text:
            return self.fallback.caption_chunk(audio_event)
        return [
            _caption_event(audio_event, event_type="caption.partial", text=text[:80], latency_ms=250),
            _caption_event(audio_event, event_type="caption.final", text=text, latency_ms=650),
        ]

    def _ready(self) -> bool:
        return bool(self.config.whisper_cpp_model) and bool(shutil.which("whisper-cli"))

    def _transcribe(self, audio_event: dict[str, Any]) -> str:
        audio_bytes = base64.b64decode(str(audio_event.get("data_b64", "")))
        if not audio_bytes:
            return ""
        with tempfile.TemporaryDirectory(prefix="signbridge-asr-") as tmp_dir:
            input_path = Path(tmp_dir) / "input.wav"
            _write_wav_input(input_path, audio_event, audio_bytes)
            result = subprocess.run(
                ["whisper-cli", "-m", self.config.whisper_cpp_model, "-f", str(input_path), "-nt"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
        return _clean_whisper_output(result.stdout)


class ElevenLabsScribeRealtimeASRProvider:
    """Activation-gated Scribe v2 Realtime interface.

    The concrete streaming client is intentionally injected by runtime work once
    the official private/on-device endpoint shape is discovered. Until then this
    adapter falls back locally without changing event contracts.
    """

    name = "elevenlabs_scribe_v2_realtime"

    def __init__(
        self,
        config: VoiceConfig,
        fallback: ASRProvider | None = None,
        streaming_adapter: Callable[[dict[str, Any]], list[dict[str, Any]]] | None = None,
    ) -> None:
        self.config = config
        self.fallback = fallback or LocalWhisperASRProvider(config)
        self.streaming_adapter = streaming_adapter

    def status(self) -> dict[str, Any]:
        if (self.config.private_elevenlabs_ready() or self.config.api_elevenlabs_ready()) and self.streaming_adapter:
            return _status(
                "captions",
                "ready",
                f"ElevenLabs {self.config.elevenlabs_asr_model} realtime ASR",
            )
        return _status(
            "captions",
            "fallback_ready",
            f"ElevenLabs {self.config.elevenlabs_asr_model} selected but streaming adapter is not attached; using local fallback",
        )

    def caption_chunk(self, audio_event: dict[str, Any]) -> list[dict[str, Any]]:
        if self.streaming_adapter:
            return self.streaming_adapter(audio_event)
        return self.fallback.caption_chunk(audio_event)


def _write_wav_input(path: Path, audio_event: dict[str, Any], audio_bytes: bytes) -> None:
    audio_format = str(audio_event.get("format", "")).lower()
    if audio_format == "wav":
        path.write_bytes(audio_bytes)
        return

    sample_rate = int(audio_event.get("sample_rate", 16000))
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)


def _clean_whisper_output(raw_output: str) -> str:
    lines = [line.strip() for line in raw_output.splitlines() if line.strip()]
    if not lines:
        return ""
    text = " ".join(lines)
    text = re.sub(r"\[[^\]]+\]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_asr_provider(config: VoiceConfig | None = None) -> ASRProvider:
    config = config or VoiceConfig.from_env()
    typed = TypedASRProvider(config.typed_caption_text)
    local = LocalWhisperASRProvider(config, fallback=typed)

    if config.asr_provider in {"elevenlabs_on_device", "elevenlabs_private"}:
        if config.private_elevenlabs_ready():
            return ElevenLabsScribeRealtimeASRProvider(config, fallback=local)
        return local

    if config.asr_provider == "elevenlabs_api":
        if config.api_elevenlabs_ready():
            return ElevenLabsScribeRealtimeASRProvider(config, fallback=local)
        return local

    if config.asr_provider in {"whisper_cpp", "local", "auto"}:
        return local

    if config.asr_provider in {"typed", "canned"} or config.offline_mode:
        return typed

    return MockASRProvider()
