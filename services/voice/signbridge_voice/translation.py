"""Gloss/token to English translation providers."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any, Protocol

from packages.contracts import validate_event

from .config import VoiceConfig
from .prompts import TOKEN_GLOSSARY, build_gloss_messages

LOW_CONFIDENCE_THRESHOLD = 0.62

DETERMINISTIC_TEMPLATES = {
    ("MY_HOME", "DAMP", "CHILD_ASTHMA"): "There is damp in my home and it is affecting my child's asthma.",
    ("INTERPRETER", "APPOINTMENT", "WRITING"): "Please arrange a BSL interpreter for the next appointment and confirm it in writing.",
    ("REPAIR", "URGENT", "CHILD"): "The repair is urgent because a child is affected.",
    ("MOULD", "BEDROOM", "CHILD"): "There is mould in the bedroom and a child is affected.",
    ("NEED", "REPAIR", "APPOINTMENT"): "I need an appointment for a repair.",
    ("COMPLAINT", "WRITING", "NEXT_STEP"): "I want to make a complaint and receive the next step in writing.",
    ("PHOTO", "EVIDENCE", "DAMP"): "I have photo evidence of damp.",
    ("NOT_UNDERSTAND", "PLEASE_REPEAT"): "I do not understand. Please repeat that.",
    ("ACCESS_SUPPORT", "INTERPRETER", "APPOINTMENT"): "I need accessible communication support and a BSL interpreter for this appointment.",
    ("INSPECTION", "DATE", "WRITING"): "Please confirm the inspection date in writing.",
}

UNSUPPORTED_FACT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"https?://",
        r"\bthe source says\b",
        r"\bpolicy\b",
        r"\blegal right\b",
        r"\byou are entitled\b",
        r"\bthe council must\b",
        r"\bguarantee(?:d|s)?\b",
        r"\bdiagnos(?:e|ed|is)\b",
        r"\bwithin \d+\b",
        r"\b20\d{2}\b",
    )
]


class GlossTranslator(Protocol):
    def translate(self, recognition_event: dict[str, Any]) -> dict[str, Any]:
        """Return a contract-valid translation.final event."""


def _clean_tokens(tokens: list[Any]) -> list[str]:
    return [str(token).strip().upper() for token in tokens if str(token).strip()]


def _event_time(recognition_event: dict[str, Any], latency_ms: int) -> int | None:
    t_ms = recognition_event.get("t_ms")
    if isinstance(t_ms, int):
        return t_ms + latency_ms
    return None


def _translation_event(
    recognition_event: dict[str, Any],
    *,
    text: str,
    confidence: float,
    latency_ms: int,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "type": "translation.final",
        "utterance_id": recognition_event["utterance_id"],
        "text": text,
        "confidence": max(0.0, min(float(confidence), 1.0)),
    }
    if recognition_event.get("session_id"):
        event["session_id"] = recognition_event["session_id"]
    t_ms = _event_time(recognition_event, latency_ms)
    if t_ms is not None:
        event["t_ms"] = t_ms
    return validate_event(event)


class TemplateGlossTranslator:
    """Deterministic demo-safe translator over the constrained vocabulary."""

    name = "template_gloss"

    def exact_template(self, tokens: list[str]) -> str | None:
        return DETERMINISTIC_TEMPLATES.get(tuple(tokens))

    def translate(self, recognition_event: dict[str, Any]) -> dict[str, Any]:
        tokens = _clean_tokens(recognition_event.get("tokens", []))
        confidence = float(recognition_event.get("confidence", 0.0))

        if confidence < LOW_CONFIDENCE_THRESHOLD:
            text = "I want to confirm what I meant before continuing."
            return _translation_event(
                recognition_event,
                text=text,
                confidence=min(confidence, 0.5),
                latency_ms=60,
            )

        exact = self.exact_template(tokens)
        if exact:
            return _translation_event(
                recognition_event,
                text=exact,
                confidence=confidence,
                latency_ms=60,
            )

        phrase_list = [TOKEN_GLOSSARY.get(token, token.replace("_", " ").lower()) for token in tokens]
        if phrase_list:
            text = "I want to confirm: " + ", ".join(phrase_list) + "."
        else:
            text = "I want to confirm what I meant before continuing."

        return _translation_event(
            recognition_event,
            text=text,
            confidence=min(confidence, 0.7),
            latency_ms=60,
        )


class LocalLLMGlossTranslator:
    """Guarded local OpenAI-compatible LLM translator with template fallback."""

    name = "local_llm_gloss"

    def __init__(self, config: VoiceConfig, fallback: TemplateGlossTranslator | None = None) -> None:
        self.config = config
        self.fallback = fallback or TemplateGlossTranslator()

    def translate(self, recognition_event: dict[str, Any]) -> dict[str, Any]:
        tokens = _clean_tokens(recognition_event.get("tokens", []))
        confidence = float(recognition_event.get("confidence", 0.0))

        exact = self.fallback.exact_template(tokens)
        if exact or confidence < LOW_CONFIDENCE_THRESHOLD or not self.config.local_llm_ready():
            return self.fallback.translate(recognition_event)

        try:
            text = self._generate_text(tokens=tokens, confidence=confidence)
        except (OSError, KeyError, TypeError, ValueError, urllib.error.URLError):
            return self.fallback.translate(recognition_event)

        if not _safe_llm_text(text):
            return self.fallback.translate(recognition_event)

        return _translation_event(
            recognition_event,
            text=text,
            confidence=min(confidence, 0.86),
            latency_ms=260,
        )

    def _generate_text(self, *, tokens: list[str], confidence: float) -> str:
        payload = {
            "model": self.config.llm_model,
            "messages": build_gloss_messages(
                tokens=tokens,
                scenario=self.config.scenario,
                confidence=confidence,
            ),
            "temperature": 0,
            "max_tokens": 120,
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.config.llm_base_url.rstrip("/") + "/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.config.llm_timeout_s) as response:
            response_payload = json.loads(response.read().decode("utf-8"))

        content = response_payload["choices"][0]["message"]["content"]
        parsed = _parse_model_json(content)
        unsupported = parsed.get("unsupported_facts") or []
        if unsupported:
            raise ValueError("Local LLM reported unsupported facts")

        text = str(parsed["text"]).strip()
        if not text:
            raise ValueError("Local LLM returned empty text")
        return text


def _parse_model_json(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("Expected JSON object from local LLM")
    return parsed


def _safe_llm_text(text: str) -> bool:
    if not text or len(text) > 240 or "\n" in text:
        return False
    return not any(pattern.search(text) for pattern in UNSUPPORTED_FACT_PATTERNS)


def build_translation_provider(config: VoiceConfig | None = None) -> GlossTranslator:
    config = config or VoiceConfig.from_env()
    if config.translation_mode == "template":
        return TemplateGlossTranslator()
    if config.llm_provider in {"", "mock", "none", "template"}:
        return TemplateGlossTranslator()
    return LocalLLMGlossTranslator(config)
