from __future__ import annotations

import time

from app.config import AppConfig
from app.models import QuestionItem
from app.retrieval.context_builder import build_retrieval_snippets
from app.retrieval.embedder import OllamaTextEmbedder, TextEmbedder
from app.retrieval.gate import RetrievalGate
from app.retrieval.loader import load_embedding_index, load_knowledge_base
from app.retrieval.models import RetrievalResult
from app.retrieval.retriever import retrieve_top_k
from app.reranker.base import BaseReranker
from app.reranker.factory import build_reranker


class RetrievalPipeline:
    def __init__(
        self,
        config: AppConfig,
        *,
        gate: RetrievalGate | None = None,
        embedder: TextEmbedder | None = None,
        reranker: BaseReranker | None = None,
    ) -> None:
        self.config = config
        self.gate = gate or RetrievalGate(config)
        self.embedder = embedder or OllamaTextEmbedder(config)
        self.reranker = reranker if reranker is not None else build_reranker(config)
        self.documents = load_knowledge_base(config.retrieval_kb_path)
        self.embedding_index = load_embedding_index(config.retrieval_embeddings_path)

    def build_snippets(self, question: QuestionItem) -> RetrievalResult:
        if not self.gate.should_retrieve(question):
            return RetrievalResult(snippets=[], retrieval_latency_ms=0.0, gate_enabled=False)

        started = time.perf_counter()
        query_vector = self.embedder.embed(self._build_query(question))
        candidates = retrieve_top_k(
            query_vector=query_vector,
            documents=self.documents,
            embeddings=self.embedding_index.records,
            top_k=self.config.retrieval_top_k,
        )
        reranker_used = False
        if self.reranker is not None and self.reranker.is_available():
            candidates = self.reranker.rerank(question, candidates, top_k=self.config.retrieval_top_k)
            reranker_used = True
        snippets = build_retrieval_snippets(candidates, max_characters=self.config.retrieval_max_characters)
        latency_ms = (time.perf_counter() - started) * 1000
        return RetrievalResult(
            snippets=snippets,
            retrieval_latency_ms=latency_ms,
            gate_enabled=True,
            reranker_used=reranker_used,
        )

    def _build_query(self, question: QuestionItem) -> str:
        return "\n".join([question.question, *question.choices])
