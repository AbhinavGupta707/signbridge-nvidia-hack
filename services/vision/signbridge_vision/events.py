"""Contract-compatible recognition event emission."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

from .recognizer import RecognitionCandidate, RecognizerConfig


@dataclass(frozen=True)
class RecognitionEmission:
    """Recognition events plus local-only fallback diagnostics."""

    events: tuple[dict[str, Any], ...]
    candidates: tuple[RecognitionCandidate, ...]
    fallback_reason: str | None = None

    @property
    def final_event(self) -> dict[str, Any] | None:
        for event in self.events:
            if event["type"] == "recognition.final":
                return event
        return None


class RecognitionEventEmitter:
    """Build shared-contract recognition events from recognizer candidates."""

    def __init__(
        self,
        *,
        config: RecognizerConfig | None = None,
        validate_contract: bool = True,
    ) -> None:
        self.config = config or RecognizerConfig()
        self.validate_contract = validate_contract

    def emit(
        self,
        candidates: list[RecognitionCandidate],
        *,
        session_id: str,
        utterance_id: str | None = None,
        t_ms: int | None = None,
    ) -> RecognitionEmission:
        if not candidates:
            return RecognitionEmission(events=(), candidates=(), fallback_reason="no_candidates")

        utterance_id = utterance_id or f"u-vision-{uuid.uuid4().hex[:8]}"
        t_ms = int(time.time() * 1000) if t_ms is None else t_ms
        best = candidates[0]
        events: list[dict[str, Any]] = []

        if best.confidence < self.config.partial_threshold:
            return RecognitionEmission(
                events=(),
                candidates=tuple(candidates),
                fallback_reason="below_partial_threshold",
            )

        partial_tokens = best.tokens[: max(1, min(2, len(best.tokens)))]
        events.append(
            self._validate(
                {
                    "type": "recognition.partial",
                    "session_id": session_id,
                    "utterance_id": utterance_id,
                    "t_ms": t_ms,
                    "tokens": list(partial_tokens),
                    "confidence": round(best.confidence, 4),
                }
            )
        )

        if best.confidence < self.config.final_threshold:
            return RecognitionEmission(
                events=tuple(events),
                candidates=tuple(candidates),
                fallback_reason="needs_confirmation_or_fallback_clip",
            )

        events.append(
            self._validate(
                {
                    "type": "recognition.final",
                    "session_id": session_id,
                    "utterance_id": utterance_id,
                    "t_ms": t_ms + 80,
                    "tokens": list(best.tokens),
                    "confidence": round(best.confidence, 4),
                }
            )
        )
        return RecognitionEmission(events=tuple(events), candidates=tuple(candidates))

    def _validate(self, event: dict[str, Any]) -> dict[str, Any]:
        if not self.validate_contract:
            return event
        try:
            from packages.contracts.signbridge_contracts import validate_event
        except Exception:
            return event

        validate_event(event)
        return event

