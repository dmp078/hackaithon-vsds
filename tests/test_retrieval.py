from __future__ import annotations

from pathlib import Path

from app.config import AppConfig
from app.models import QuestionItem
from app.retrieval.context_builder import build_retrieval_snippets
from app.retrieval.gate import RetrievalGate
from app.retrieval.loader import load_embedding_index, load_knowledge_base
from app.retrieval.models import EmbeddingRecord, KnowledgeDocument
from app.retrieval.retriever import cosine_similarity, retrieve_top_k


def test_retrieval_gate_skips_short_arithmetic() -> None:
    gate = RetrievalGate(AppConfig())
    question = QuestionItem(qid="q1", question="2 + 2 bằng bao nhiêu?", choices=["3", "4", "5"], category="mathematics")

    assert gate.should_retrieve(question) is False


def test_retrieval_gate_allows_formula_heavy_math_question() -> None:
    gate = RetrievalGate(AppConfig(retrieval_mode="on"))
    question = QuestionItem(
        qid="q2",
        question="Hàm số bậc hai có công thức nghiệm như thế nào và biệt thức delta được tính ra sao?",
        choices=["A", "B", "C", "D"],
        category="mathematics",
    )

    assert gate.should_retrieve(question) is True


def test_load_knowledge_base_and_embedding_index(tmp_path: Path) -> None:
    kb_path = tmp_path / "kb.json"
    embeddings_path = tmp_path / "embeddings.json"
    kb_path.write_text(
        '[{"id":"doc_1","category":"mathematics","title":"Công thức nghiệm","keywords":["delta"],"content":"x = ..."}]',
        encoding="utf-8",
    )
    embeddings_path.write_text(
        '{"model":"bge-m3","dimension":3,"records":[{"id":"doc_1","vector":[1.0,0.0,0.0]}]}',
        encoding="utf-8",
    )

    documents = load_knowledge_base(kb_path)
    index = load_embedding_index(embeddings_path)

    assert documents[0].title == "Công thức nghiệm"
    assert index.model == "bge-m3"
    assert index.vectors_by_id["doc_1"] == [1.0, 0.0, 0.0]


def test_retrieve_top_k_prefers_highest_cosine_similarity() -> None:
    documents = [
        KnowledgeDocument(id="doc_1", category="mathematics", title="A", keywords=["a"], content="A"),
        KnowledgeDocument(id="doc_2", category="physics_engineering", title="B", keywords=["b"], content="B"),
    ]
    embeddings = [
        EmbeddingRecord(id="doc_1", vector=[1.0, 0.0, 0.0]),
        EmbeddingRecord(id="doc_2", vector=[0.0, 1.0, 0.0]),
    ]

    results = retrieve_top_k(query_vector=[0.9, 0.1, 0.0], documents=documents, embeddings=embeddings, top_k=1)

    assert results[0].document.id == "doc_1"
    assert results[0].score > 0.9


def test_cosine_similarity_handles_zero_vectors() -> None:
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_context_builder_limits_total_size() -> None:
    snippets = build_retrieval_snippets(
        [
            KnowledgeDocument(
                id="doc_1",
                category="mathematics",
                title="Doc 1",
                keywords=["quadratic"],
                content="A" * 400,
            ),
            KnowledgeDocument(
                id="doc_2",
                category="physics_engineering",
                title="Doc 2",
                keywords=["force"],
                content="B" * 400,
            ),
        ],
        max_characters=450,
    )

    assert len(snippets) == 1
    assert "Doc 1" in snippets[0]
