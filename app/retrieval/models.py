from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class KnowledgeDocument:
    id: str
    category: str
    title: str
    keywords: list[str]
    content: str


@dataclass(slots=True)
class EmbeddingRecord:
    id: str
    vector: list[float]


@dataclass(slots=True)
class EmbeddingIndex:
    model: str
    dimension: int
    records: list[EmbeddingRecord]

    @property
    def vectors_by_id(self) -> dict[str, list[float]]:
        return {record.id: record.vector for record in self.records}


@dataclass(slots=True)
class RetrievedDocument:
    document: KnowledgeDocument
    score: float
    source: str = "cosine"


@dataclass(slots=True)
class RetrievalResult:
    snippets: list[str]
    retrieval_latency_ms: float
    gate_enabled: bool
    reranker_used: bool = False
