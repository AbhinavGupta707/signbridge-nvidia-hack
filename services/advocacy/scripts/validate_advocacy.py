#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = SCRIPT_DIR.parent
REPO_ROOT = PACKAGE_DIR.parent.parent
sys.path.insert(0, str(PACKAGE_DIR))
sys.path.insert(0, str(REPO_ROOT))

from signbridge_advocacy import AdvocacyPipeline, LocalRetriever
from signbridge_advocacy.paths import DEFAULT_INDEX_PATH, DEFAULT_MANIFEST_PATH
from packages.contracts import validate_event


def validate_manifest() -> None:
    manifest = json.loads(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))
    source_ids = set()
    for source in manifest["sources"]:
        source_id = source["source_id"]
        if source_id in source_ids:
            raise AssertionError(f"Duplicate source_id {source_id}")
        source_ids.add(source_id)
        for field in ("title", "publisher", "url", "status", "verified_on"):
            if not source.get(field):
                raise AssertionError(f"{source_id} missing {field}")


def validate_retrieval() -> None:
    retriever = LocalRetriever()
    results = retriever.search("child asthma mould bedroom emergency", limit=3, policy_only=True)
    if not results:
        raise AssertionError("Expected retrieval result for child asthma query")
    if results[0].chunk.chunk_id != "govuk-landlord-child-asthma":
        raise AssertionError(f"Unexpected top chunk: {results[0].chunk.chunk_id}")


def validate_events() -> None:
    pipeline = AdvocacyPipeline()
    generated = pipeline.run_turn(
        "There is mould in my child's bedroom and asthma is worse. I need BSL written updates.",
        session_id="validate-001",
        utterance_id="u-validate",
    )
    if not generated["policy_cards"]:
        raise AssertionError("Expected policy cards")
    if not generated["question_prompts"]:
        raise AssertionError("Expected question prompts")
    for card in generated["policy_cards"]:
        validate_event(card)
        for field in ("claim", "source_title", "source_url", "quote", "citations"):
            if not card.get(field):
                raise AssertionError(f"Policy card {card['id']} missing {field}")
        for citation in card["citations"]:
            for field in ("source_title", "source_url", "quote", "verified"):
                if field not in citation or citation[field] in ("", None):
                    raise AssertionError(f"Policy card {card['id']} citation missing {field}")
    for prompt in generated["question_prompts"]:
        validate_event(prompt)


def validate_index_exists() -> None:
    if not DEFAULT_INDEX_PATH.exists():
        raise AssertionError(f"Missing index file: {DEFAULT_INDEX_PATH}")
    if not DEFAULT_INDEX_PATH.read_text(encoding="utf-8").strip():
        raise AssertionError("Index file is empty")


def main() -> None:
    validate_manifest()
    validate_index_exists()
    validate_retrieval()
    validate_events()
    print("Advocacy validation passed")


if __name__ == "__main__":
    main()
