"""Provider bundle compatible with orchestrator event flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from packages.contracts import validate_event

from .asr import ASRProvider, build_asr_provider
from .config import VoiceConfig
from .translation import GlossTranslator, build_translation_provider
from .tts import TTSProvider, build_tts_provider


@dataclass
class VoiceProviders:
    """Provider bundle with orchestrator-compatible method boundaries."""

    translation: GlossTranslator
    tts: TTSProvider
    captions: ASRProvider

    def status_events(self) -> list[dict[str, Any]]:
        return [
            validate_event(
                {
                    "type": "system.status",
                    "component": "translation",
                    "status": "ready",
                    "detail": getattr(self.translation, "name", "gloss_translator"),
                }
            ),
            self.tts.status(),
            self.captions.status(),
        ]

    def translate_and_speak(self, recognition_event: dict[str, Any]) -> list[dict[str, Any]]:
        translation = self.translation.translate(recognition_event)
        speech = self.tts.synthesize(translation)
        return [translation, speech]

    def caption_chunk(self, audio_event: dict[str, Any]) -> list[dict[str, Any]]:
        return self.captions.caption_chunk(audio_event)


def build_voice_providers(config: VoiceConfig | None = None) -> VoiceProviders:
    config = config or VoiceConfig.from_env()
    return VoiceProviders(
        translation=build_translation_provider(config),
        tts=build_tts_provider(config),
        captions=build_asr_provider(config),
    )
