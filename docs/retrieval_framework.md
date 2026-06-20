# Retrieval Framework Overview

## Goal

This retrieval layer is an optional framework for benchmarking whether curated offline reference snippets improve generalization on unseen questions without changing the stable production inference path.

## Design constraints

- `retrieval=off` must preserve current behavior.
- Document embeddings are generated offline only.
- Inference never regenerates document embeddings.
- Query embedding is isolated behind one interface.
- Retrieval logic is modular so the corpus, embedder, or reranker can be replaced later.

## Components

- `app/retrieval/loader.py`
  - Loads `knowledge_base/reference_documents.json`
  - Loads `embeddings/bge_m3_reference_documents.json`

- `app/retrieval/gate.py`
  - Heuristic gate for deciding whether retrieval is likely to help
  - Skips short arithmetic, low-information prompts, and categories outside the initial corpus focus

- `app/retrieval/embedder.py`
  - Defines the text-embedding interface
  - Current implementation uses local Ollama with `bge-m3`

- `app/retrieval/retriever.py`
  - Pure Python cosine-similarity top-k retrieval over precomputed document vectors

- `app/retrieval/context_builder.py`
  - Packs a few retrieved docs into short snippets for prompt injection

- `app/retrieval/pipeline.py`
  - Orchestrates gate -> query embedding -> retrieval -> optional reranker -> snippet building

- `app/reranker/`
  - Defines an optional reranker interface
  - Current implementation is intentionally a no-op fallback because no compatible local Qwen reranker is available in this environment

## Inference flow

### Retrieval off

`Question -> current heuristic/LLM pipeline -> prediction`

### Retrieval on

`Question -> current heuristic/LLM pipeline`

If the question reaches the LLM solver and the retrieval gate approves:

`-> query embedding`

`-> top-k cosine retrieval from offline vectors`

`-> optional rerank if available`

`-> short snippet injection into the existing prompt`

`-> existing LLM generation path`

## Offline indexing

1. `scripts/build_kb.py`
   - Generates the small curated JSON corpus

2. `scripts/build_embeddings.py`
   - Uses local `bge-m3` to create and store document embeddings

## Future expansion

The framework is designed so later work can:

- replace the 100-200 doc starter corpus with a much larger corpus
- swap the embedding backend without changing retrieval orchestration
- add a real local reranker implementation
- benchmark Qwen3.5 and Gemma-4 through the same retrieval layer
- experiment with different retrieval strategies without changing the stable inference pipeline
