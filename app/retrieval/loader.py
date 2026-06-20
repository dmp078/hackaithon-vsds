from __future__ import annotations

import json
from pathlib import Path

from app.retrieval.models import EmbeddingIndex, EmbeddingRecord, KnowledgeDocument


def load_knowledge_base(path: Path) -> list[KnowledgeDocument]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        KnowledgeDocument(
            id=str(item["id"]),
            category=str(item["category"]),
            title=str(item["title"]),
            keywords=[str(keyword) for keyword in item.get("keywords", [])],
            content=str(item["content"]),
        )
        for item in payload
    ]


def load_embedding_index(path: Path) -> EmbeddingIndex:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = [
        EmbeddingRecord(id=str(item["id"]), vector=[float(value) for value in item["vector"]])
        for item in payload.get("records", [])
    ]
    return EmbeddingIndex(
        model=str(payload.get("model", "")),
        dimension=int(payload.get("dimension", 0)),
        records=records,
    )
