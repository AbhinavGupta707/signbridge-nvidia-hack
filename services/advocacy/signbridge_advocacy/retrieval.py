from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .paths import DEFAULT_INDEX_PATH, DEFAULT_MANIFEST_PATH


TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    publisher: str
    url: str
    source_type: str
    status: str
    verified_on: str | None
    policy_claim_allowed: bool
    notes: str = ""


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_id: str
    title: str
    text: str
    quote: str
    source_url: str
    locator: str
    tags: tuple[str, ...]
    claim_type: str
    verified: bool


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    source: Source
    score: float

    def citation(self) -> dict[str, Any]:
        return {
            "source_id": self.source.source_id,
            "source_title": self.source.title,
            "publisher": self.source.publisher,
            "source_url": self.chunk.source_url or self.source.url,
            "quote": self.chunk.quote,
            "locator": self.chunk.locator,
            "verified": self.chunk.verified and self.source.status == "verified",
            "verified_on": self.source.verified_on,
        }


class LocalRetriever:
    """Small offline BM25 retriever over verified Signbridge policy chunks."""

    def __init__(
        self,
        index_path: Path | str = DEFAULT_INDEX_PATH,
        manifest_path: Path | str = DEFAULT_MANIFEST_PATH,
    ) -> None:
        self.index_path = Path(index_path)
        self.manifest_path = Path(manifest_path)
        self.sources = self._load_sources(self.manifest_path)
        self.chunks = self._load_chunks(self.index_path)
        self._doc_tokens = [tokenize(" ".join([c.title, c.text, " ".join(c.tags)])) for c in self.chunks]
        self._doc_freq = self._build_doc_freq(self._doc_tokens)
        self._avg_len = (
            sum(len(tokens) for tokens in self._doc_tokens) / len(self._doc_tokens)
            if self._doc_tokens
            else 1.0
        )

    @staticmethod
    def _load_sources(path: Path) -> dict[str, Source]:
        data = json.loads(path.read_text(encoding="utf-8"))
        sources: dict[str, Source] = {}
        for item in data["sources"]:
            sources[item["source_id"]] = Source(
                source_id=item["source_id"],
                title=item["title"],
                publisher=item["publisher"],
                url=item["url"],
                source_type=item["source_type"],
                status=item["status"],
                verified_on=item.get("verified_on"),
                policy_claim_allowed=bool(item.get("policy_claim_allowed")),
                notes=item.get("notes", ""),
            )
        return sources

    @staticmethod
    def _load_chunks(path: Path) -> list[Chunk]:
        chunks: list[Chunk] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            chunks.append(
                Chunk(
                    chunk_id=item["chunk_id"],
                    source_id=item["source_id"],
                    title=item["title"],
                    text=item["text"],
                    quote=item["quote"],
                    source_url=item["source_url"],
                    locator=item.get("locator", ""),
                    tags=tuple(item.get("tags", [])),
                    claim_type=item.get("claim_type", "unknown"),
                    verified=bool(item.get("verified")),
                )
            )
        return chunks

    @staticmethod
    def _build_doc_freq(token_lists: Iterable[list[str]]) -> Counter[str]:
        doc_freq: Counter[str] = Counter()
        for tokens in token_lists:
            doc_freq.update(set(tokens))
        return doc_freq

    def source_for(self, source_id: str) -> Source:
        return self.sources[source_id]

    def chunk_by_id(self, chunk_id: str) -> Chunk:
        for chunk in self.chunks:
            if chunk.chunk_id == chunk_id:
                return chunk
        raise KeyError(f"Unknown chunk_id: {chunk_id}")

    def citation_for_chunk_id(self, chunk_id: str) -> dict[str, Any]:
        chunk = self.chunk_by_id(chunk_id)
        source = self.source_for(chunk.source_id)
        return SearchResult(chunk=chunk, source=source, score=1.0).citation()

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        policy_only: bool = False,
        include_context: bool = True,
    ) -> list[SearchResult]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores: list[SearchResult] = []
        total_docs = max(len(self.chunks), 1)
        query_counts = Counter(query_tokens)
        for chunk, doc_tokens in zip(self.chunks, self._doc_tokens, strict=True):
            source = self.source_for(chunk.source_id)
            if policy_only and not source.policy_claim_allowed:
                continue
            if not include_context and chunk.claim_type.endswith("_context"):
                continue
            score = self._bm25(query_counts, doc_tokens, total_docs)
            if score > 0:
                scores.append(SearchResult(chunk=chunk, source=source, score=score))
        scores.sort(key=lambda result: result.score, reverse=True)
        return scores[:limit]

    def _bm25(self, query_counts: Counter[str], doc_tokens: list[str], total_docs: int) -> float:
        counts = Counter(doc_tokens)
        doc_len = max(len(doc_tokens), 1)
        k1 = 1.4
        b = 0.75
        score = 0.0
        for term, query_weight in query_counts.items():
            freq = counts.get(term, 0)
            if not freq:
                continue
            doc_freq = self._doc_freq.get(term, 0)
            idf = math.log(1 + (total_docs - doc_freq + 0.5) / (doc_freq + 0.5))
            denom = freq + k1 * (1 - b + b * doc_len / self._avg_len)
            score += query_weight * idf * ((freq * (k1 + 1)) / denom)
        return round(score, 6)
