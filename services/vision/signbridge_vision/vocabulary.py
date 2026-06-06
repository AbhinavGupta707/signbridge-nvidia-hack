"""Constrained vocabulary for the Signbridge housing-repair demo."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


VOCABULARY_PATH = Path(__file__).resolve().parents[1] / "vocabulary" / "housing_repair_vocabulary.json"


@dataclass(frozen=True)
class VocabularyEntry:
    """One recognisable phrase in the constrained demo vocabulary."""

    phrase_id: str
    display: str
    tokens: tuple[str, ...]
    english_hint: str
    scenario: str = "housing_repair"
    needs_confirmation: bool = True
    safety_note: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "VocabularyEntry":
        tokens = payload.get("tokens")
        if not isinstance(tokens, list) or not tokens or not all(isinstance(token, str) for token in tokens):
            raise ValueError(f"Vocabulary entry {payload.get('phrase_id')} needs a non-empty string token list")

        return cls(
            phrase_id=str(payload["phrase_id"]),
            display=str(payload["display"]),
            tokens=tuple(tokens),
            english_hint=str(payload["english_hint"]),
            scenario=str(payload.get("scenario", "housing_repair")),
            needs_confirmation=bool(payload.get("needs_confirmation", True)),
            safety_note=(
                str(payload["safety_note"])
                if payload.get("safety_note") is not None
                else None
            ),
        )


class Vocabulary:
    """Lookup and validation helper for a deliberately small phrase set."""

    def __init__(self, entries: Iterable[VocabularyEntry]) -> None:
        self.entries = tuple(entries)
        if not 20 <= len(self.entries) <= 35:
            raise ValueError(f"Constrained vocabulary must contain 20-35 entries; got {len(self.entries)}")

        ids = [entry.phrase_id for entry in self.entries]
        if len(set(ids)) != len(ids):
            raise ValueError("Vocabulary phrase_id values must be unique")

        self._by_id = {entry.phrase_id: entry for entry in self.entries}
        self._by_tokens = {entry.tokens: entry for entry in self.entries}

    @classmethod
    def from_json(cls, path: Path) -> "Vocabulary":
        with path.open("r", encoding="utf-8") as vocabulary_file:
            payload = json.load(vocabulary_file)

        entries_payload = payload.get("entries")
        if not isinstance(entries_payload, list):
            raise ValueError(f"{path} must contain an entries array")

        return cls(VocabularyEntry.from_dict(entry) for entry in entries_payload)

    def get(self, phrase_id: str) -> VocabularyEntry:
        return self._by_id[phrase_id]

    def find_by_tokens(self, tokens: Iterable[str]) -> VocabularyEntry | None:
        return self._by_tokens.get(tuple(tokens))

    def tokens_for(self, phrase_id: str) -> tuple[str, ...]:
        return self.get(phrase_id).tokens

    def phrase_ids(self) -> tuple[str, ...]:
        return tuple(entry.phrase_id for entry in self.entries)


def load_housing_repair_vocabulary(path: Path = VOCABULARY_PATH) -> Vocabulary:
    """Load the fixed housing repair / damp and mould demo vocabulary."""

    return Vocabulary.from_json(path)

