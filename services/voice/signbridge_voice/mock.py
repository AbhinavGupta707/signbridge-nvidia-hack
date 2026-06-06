"""Mock voice provider bundle for integration wiring."""

from __future__ import annotations

from dataclasses import dataclass, field

from .asr import MockASRProvider
from .translation import TemplateGlossTranslator
from .tts import MockTTSProvider


@dataclass
class MockVoiceProviders:
    """Same attribute names used by the orchestrator mock layer."""

    translation: TemplateGlossTranslator = field(default_factory=TemplateGlossTranslator)
    tts: MockTTSProvider = field(default_factory=MockTTSProvider)
    captions: MockASRProvider = field(default_factory=MockASRProvider)

