#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PACKAGE_DIR))

from signbridge_advocacy.paths import DEFAULT_INDEX_PATH, DEFAULT_MANIFEST_PATH, DEFAULT_SEED_PATH


def load_manifest_source_ids() -> set[str]:
    manifest = json.loads(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))
    return {source["source_id"] for source in manifest["sources"]}


def build_index() -> Path:
    source_ids = load_manifest_source_ids()
    seed = json.loads(DEFAULT_SEED_PATH.read_text(encoding="utf-8"))
    DEFAULT_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    for chunk in seed["chunks"]:
        if chunk["source_id"] not in source_ids:
            raise ValueError(f"Chunk {chunk['chunk_id']} has unknown source_id {chunk['source_id']}")
        for required in ("chunk_id", "source_id", "title", "text", "quote", "source_url", "verified"):
            if required not in chunk or chunk[required] in ("", None):
                raise ValueError(f"Chunk {chunk.get('chunk_id')} missing {required}")
        lines.append(json.dumps(chunk, sort_keys=True))

    DEFAULT_INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return DEFAULT_INDEX_PATH


def main() -> None:
    output = build_index()
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
