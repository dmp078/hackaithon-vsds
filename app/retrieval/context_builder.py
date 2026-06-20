from __future__ import annotations

from app.retrieval.models import KnowledgeDocument, RetrievedDocument


def build_retrieval_snippets(
    documents: list[KnowledgeDocument] | list[RetrievedDocument],
    *,
    max_characters: int,
) -> list[str]:
    snippets: list[str] = []
    total_characters = 0
    for item in documents:
        document = item.document if isinstance(item, RetrievedDocument) else item
        snippet = (
            f"[{document.category}] {document.title}\n"
            f"Từ khóa: {', '.join(document.keywords[:6])}\n"
            f"{document.content}"
        ).strip()
        if total_characters + len(snippet) > max_characters:
            break
        snippets.append(snippet)
        total_characters += len(snippet)
    return snippets
