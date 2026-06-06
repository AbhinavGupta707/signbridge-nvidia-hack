"""Configuration and activation gates for Signbridge voice providers."""

from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass, field
from urllib.parse import urlparse

TRUE_VALUES = {"1", "true", "yes", "on"}


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


def _env_float(name: str, default: float) -> float:
    raw_value = os.environ.get(name)
    if not raw_value:
        return default
    try:
        return float(raw_value)
    except ValueError:
        return default


def is_local_or_private_url(url: str) -> bool:
    """Return true for localhost, LAN, and private deployment URLs."""

    if not url:
        return False

    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        return False

    if host in {"localhost", "0.0.0.0"} or host.endswith(".local"):
        return True

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False

    return address.is_loopback or address.is_private or address.is_link_local


@dataclass(frozen=True)
class VoiceConfig:
    """Runtime config with no secret values in status summaries."""

    scenario: str = "housing_repair"
    llm_provider: str = "mock"
    llm_base_url: str = "http://localhost:8080/v1"
    llm_model: str = "local-open-model"
    llm_timeout_s: float = 2.0
    translation_mode: str = "hybrid"

    tts_provider: str = "mock"
    asr_provider: str = "mock"
    offline_mode: bool = False
    allow_network_egress: bool = False

    elevenlabs_on_device_available: bool = False
    elevenlabs_private_base_url: str = ""
    elevenlabs_api_key: str = field(default="", repr=False)
    elevenlabs_tts_model: str = "eleven_flash_v2_5"
    elevenlabs_asr_model: str = "scribe_v2_realtime"
    elevenlabs_voice_id: str = ""

    canned_voice_dir: str = "demo/voice_samples"
    piper_voice_model: str = ""
    kokoro_model_path: str = ""
    whisper_cpp_model: str = ""
    faster_whisper_model: str = ""
    typed_caption_text: str = ""

    @classmethod
    def from_env(cls) -> "VoiceConfig":
        return cls(
            scenario=os.environ.get("SIGNBRIDGE_SCENARIO", "housing_repair").strip(),
            llm_provider=os.environ.get("LLM_PROVIDER", "mock").strip().lower(),
            llm_base_url=os.environ.get("LLM_BASE_URL", "http://localhost:8080/v1").strip(),
            llm_model=os.environ.get("LLM_MODEL", "local-open-model").strip(),
            llm_timeout_s=_env_float("LLM_TIMEOUT_S", 2.0),
            translation_mode=os.environ.get("SIGNBRIDGE_TRANSLATION_MODE", "hybrid").strip().lower(),
            tts_provider=os.environ.get("TTS_PROVIDER", "mock").strip().lower(),
            asr_provider=os.environ.get("ASR_PROVIDER", "mock").strip().lower(),
            offline_mode=env_bool("OFFLINE_MODE", False),
            allow_network_egress=env_bool("ALLOW_NETWORK_EGRESS", False),
            elevenlabs_on_device_available=env_bool("ELEVENLABS_ON_DEVICE_AVAILABLE", False),
            elevenlabs_private_base_url=os.environ.get("ELEVENLABS_PRIVATE_BASE_URL", "").strip(),
            elevenlabs_api_key=os.environ.get("ELEVENLABS_API_KEY", ""),
            elevenlabs_tts_model=os.environ.get("ELEVENLABS_TTS_MODEL", "eleven_flash_v2_5").strip(),
            elevenlabs_asr_model=os.environ.get("ELEVENLABS_ASR_MODEL", "scribe_v2_realtime").strip(),
            elevenlabs_voice_id=os.environ.get("ELEVENLABS_VOICE_ID", "").strip(),
            canned_voice_dir=os.environ.get("CANNED_VOICE_DIR", "demo/voice_samples").strip(),
            piper_voice_model=os.environ.get("PIPER_VOICE_MODEL", "").strip(),
            kokoro_model_path=os.environ.get("KOKORO_MODEL_PATH", "").strip(),
            whisper_cpp_model=os.environ.get("WHISPER_CPP_MODEL", "").strip(),
            faster_whisper_model=os.environ.get("FASTER_WHISPER_MODEL", "").strip(),
            typed_caption_text=os.environ.get("SIGNBRIDGE_TYPED_CAPTION", "").strip(),
        )

    def private_elevenlabs_ready(self) -> bool:
        return self.elevenlabs_on_device_available and bool(self.elevenlabs_private_base_url)

    def api_elevenlabs_ready(self) -> bool:
        return bool(self.elevenlabs_api_key) and self.allow_network_egress and not self.offline_mode

    def local_llm_ready(self) -> bool:
        if self.llm_provider in {"", "mock", "none", "template"}:
            return False
        if not self.llm_base_url or not self.llm_model:
            return False
        return self.allow_network_egress or is_local_or_private_url(self.llm_base_url)

    def summary(self) -> dict[str, object]:
        """Return non-secret provider state for health/debug surfaces."""

        return {
            "llm_provider": self.llm_provider,
            "scenario": self.scenario,
            "llm_model": self.llm_model,
            "llm_endpoint_local_or_private": is_local_or_private_url(self.llm_base_url),
            "translation_mode": self.translation_mode,
            "tts_provider": self.tts_provider,
            "asr_provider": self.asr_provider,
            "offline_mode": self.offline_mode,
            "allow_network_egress": self.allow_network_egress,
            "elevenlabs_on_device_available": self.elevenlabs_on_device_available,
            "elevenlabs_private_base_url_set": bool(self.elevenlabs_private_base_url),
            "elevenlabs_api_key_set": bool(self.elevenlabs_api_key),
        }
