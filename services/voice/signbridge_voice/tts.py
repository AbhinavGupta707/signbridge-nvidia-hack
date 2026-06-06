"""TTS provider interfaces and activation-gated implementations."""

from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
import wave
from dataclasses import replace
from io import BytesIO
from pathlib import Path
from typing import Any, Protocol

from packages.contracts import validate_event

from .config import VoiceConfig


class TTSProvider(Protocol):
    name: str

    def status(self) -> dict[str, Any]:
        """Return a system.status event."""

    def synthesize(self, translation_event: dict[str, Any]) -> dict[str, Any]:
        """Return a tts.audio event."""


def silent_wav_b64(duration_ms: int = 220, sample_rate: int = 16000) -> str:
    frame_count = max(1, int(sample_rate * duration_ms / 1000))
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frame_count)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _audio_event(
    translation_event: dict[str, Any],
    *,
    audio_b64: str,
    audio_format: str,
    latency_ms: int,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "type": "tts.audio",
        "utterance_id": translation_event["utterance_id"],
        "format": audio_format,
        "data_b64": audio_b64,
    }
    if translation_event.get("session_id"):
        event["session_id"] = translation_event["session_id"]
    t_ms = translation_event.get("t_ms")
    if isinstance(t_ms, int):
        event["t_ms"] = t_ms + latency_ms
    return validate_event(event)


def _status(component: str, status: str, detail: str) -> dict[str, Any]:
    return validate_event(
        {
            "type": "system.status",
            "component": component,
            "status": status,
            "detail": detail,
        }
    )


class MockTTSProvider:
    """Contract-compatible audio placeholder for integration wiring."""

    name = "mock_tts"

    def status(self) -> dict[str, Any]:
        return _status("tts", "mock_ready", "mock wav placeholder; not a spoken TTS proof")

    def synthesize(self, translation_event: dict[str, Any]) -> dict[str, Any]:
        return _audio_event(
            translation_event,
            audio_b64=silent_wav_b64(),
            audio_format="wav",
            latency_ms=40,
        )


class CannedTTSProvider:
    """Use pre-rendered local audio when a matching file is available."""

    name = "canned_tts"

    def __init__(self, directory: str, fallback: TTSProvider | None = None) -> None:
        self.directory = Path(directory)
        self.fallback = fallback or MockTTSProvider()

    def status(self) -> dict[str, Any]:
        return _status("tts", "fallback_ready", f"canned local audio from {self.directory}")

    def synthesize(self, translation_event: dict[str, Any]) -> dict[str, Any]:
        for path in self._candidate_paths(translation_event):
            if path.exists():
                audio_format = path.suffix.lstrip(".") or "wav"
                return _audio_event(
                    translation_event,
                    audio_b64=base64.b64encode(path.read_bytes()).decode("ascii"),
                    audio_format=audio_format,
                    latency_ms=30,
                )
        return self.fallback.synthesize(translation_event)

    def _candidate_paths(self, translation_event: dict[str, Any]) -> list[Path]:
        utterance_id = str(translation_event.get("utterance_id", ""))
        text = str(translation_event.get("text", ""))
        text_key = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
        return [
            self.directory / f"{utterance_id}.wav",
            self.directory / f"{utterance_id}.mp3",
            self.directory / f"{text_key}.wav",
            self.directory / f"{text_key}.mp3",
        ]


class LocalCommandTTSProvider:
    """Offline local TTS using installed command-line engines."""

    name = "local_command_tts"

    def __init__(self, config: VoiceConfig, fallback: TTSProvider | None = None) -> None:
        self.config = config
        self.fallback = fallback or MockTTSProvider()

    def status(self) -> dict[str, Any]:
        engine = self._selected_engine()
        if engine:
            return _status("tts", "ready", f"local {engine} TTS")
        return _status("tts", "fallback_ready", "no local TTS command found; using mock wav placeholder")

    def synthesize(self, translation_event: dict[str, Any]) -> dict[str, Any]:
        text = str(translation_event.get("text", "")).strip()
        if not text:
            return self.fallback.synthesize(translation_event)

        try:
            audio = self._synthesize_wav(text)
        except (OSError, subprocess.SubprocessError):
            return self.fallback.synthesize(translation_event)

        if not audio:
            return self.fallback.synthesize(translation_event)

        return _audio_event(
            translation_event,
            audio_b64=base64.b64encode(audio).decode("ascii"),
            audio_format="wav",
            latency_ms=220,
        )

    def _selected_engine(self) -> str | None:
        provider = self.config.tts_provider
        if provider == "piper" and shutil.which("piper") and self.config.piper_voice_model:
            return "piper"
        if provider in {"espeak_ng", "local", "auto"} and shutil.which("espeak-ng"):
            return "espeak-ng"
        if provider in {"piper", "local", "auto"} and shutil.which("piper") and self.config.piper_voice_model:
            return "piper"
        return None

    def _synthesize_wav(self, text: str) -> bytes:
        engine = self._selected_engine()
        if not engine:
            return b""

        with tempfile.TemporaryDirectory(prefix="signbridge-tts-") as tmp_dir:
            output_path = Path(tmp_dir) / "speech.wav"
            if engine == "piper":
                subprocess.run(
                    ["piper", "--model", self.config.piper_voice_model, "--output_file", str(output_path)],
                    input=text,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            elif engine == "espeak-ng":
                subprocess.run(
                    ["espeak-ng", "-w", str(output_path), text],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            return output_path.read_bytes() if output_path.exists() else b""


class ElevenLabsTTSProvider:
    """ElevenLabs TTS adapter, selected only after activation gates pass."""

    name = "elevenlabs_tts"

    def __init__(
        self,
        config: VoiceConfig,
        *,
        base_url: str,
        api_key: str = "",
        fallback: TTSProvider | None = None,
    ) -> None:
        self.config = config
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.fallback = fallback or LocalCommandTTSProvider(config)

    def status(self) -> dict[str, Any]:
        if not self.config.elevenlabs_voice_id:
            return _status("tts", "fallback_ready", "ElevenLabs selected but ELEVENLABS_VOICE_ID is unset")
        return _status("tts", "ready", f"ElevenLabs {self.config.elevenlabs_tts_model}")

    def synthesize(self, translation_event: dict[str, Any]) -> dict[str, Any]:
        if not self.config.elevenlabs_voice_id:
            return self.fallback.synthesize(translation_event)

        text = str(translation_event.get("text", "")).strip()
        if not text:
            return self.fallback.synthesize(translation_event)

        try:
            audio = self._request_audio(text)
        except (OSError, ValueError, urllib.error.URLError):
            return self.fallback.synthesize(translation_event)

        return _audio_event(
            translation_event,
            audio_b64=base64.b64encode(audio).decode("ascii"),
            audio_format="mp3",
            latency_ms=180,
        )

    def _request_audio(self, text: str) -> bytes:
        api_base = self.base_url if self.base_url.endswith("/v1") else f"{self.base_url}/v1"
        endpoint = f"{api_base}/text-to-speech/{self.config.elevenlabs_voice_id}"
        payload = {
            "text": text,
            "model_id": self.config.elevenlabs_tts_model,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["xi-api-key"] = self.api_key

        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=4) as response:
            return response.read()


def build_tts_provider(config: VoiceConfig | None = None) -> TTSProvider:
    config = config or VoiceConfig.from_env()
    auto_local_config = replace(config, tts_provider="auto")
    local_fallback: TTSProvider
    if config.tts_provider == "canned":
        local_fallback = CannedTTSProvider(config.canned_voice_dir)
    else:
        local_fallback = LocalCommandTTSProvider(config)

    if config.tts_provider in {"elevenlabs_on_device", "elevenlabs_private"}:
        local_fallback = LocalCommandTTSProvider(auto_local_config)
        if config.private_elevenlabs_ready():
            return ElevenLabsTTSProvider(
                config,
                base_url=config.elevenlabs_private_base_url,
                fallback=local_fallback,
            )
        return local_fallback

    if config.tts_provider == "elevenlabs_api":
        local_fallback = LocalCommandTTSProvider(auto_local_config)
        if config.api_elevenlabs_ready():
            return ElevenLabsTTSProvider(
                config,
                base_url="https://api.elevenlabs.io",
                api_key=config.elevenlabs_api_key,
                fallback=local_fallback,
            )
        return local_fallback

    if config.tts_provider in {"piper", "espeak_ng", "local", "auto", "canned"}:
        return local_fallback

    if config.offline_mode:
        return local_fallback

    return MockTTSProvider()
