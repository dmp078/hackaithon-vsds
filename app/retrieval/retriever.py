from __future__ import annotations

import math

from app.retrieval.models import EmbeddingRecord, KnowledgeDocument, RetrievedDocument


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Vectors must have the same dimension")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    return dot / (left_norm * right_norm)


def retrieve_top_k(
    *,
    query_vector: list[float],
    documents: list[KnowledgeDocument],
    embeddings: list[EmbeddingRecord],
    top_k: int,
) -> list[RetrievedDocument]:
    document_by_id = {document.id: document for document in documents}
    scored: list[RetrievedDocument] = []
    for record in embeddings:
        document = document_by_id.get(record.id)
        if document is None:
            continue
        scored.append(
            RetrievedDocument(
                document=document,
                score=cosine_similarity(query_vector, record.vector),
            )
        )
    return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]
