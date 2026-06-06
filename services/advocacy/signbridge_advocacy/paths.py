from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_MANIFEST_PATH = (
    REPO_ROOT / "docs" / "sources" / "city_london_housing_repair_source_manifest.json"
)
DEFAULT_SEED_PATH = (
    REPO_ROOT / "services" / "advocacy" / "corpus" / "verified_source_notes.json"
)
RAW_SEED_MIRROR_PATH = (
    REPO_ROOT / "data" / "raw" / "advocacy" / "housing_repair" / "verified_source_notes.json"
)
DEFAULT_INDEX_PATH = (
    REPO_ROOT / "services" / "advocacy" / "index" / "housing_repair_chunks.jsonl"
)
DEFAULT_EXAMPLES_DIR = REPO_ROOT / "services" / "advocacy" / "examples"
