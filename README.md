# hackaithon-mcq-agent

Vietnamese multiple-choice QA agent for a technical AI competition. The current implementation is a local MVP for bảng C: batch input, deterministic offline verification, native Ollama inference, structured parsing, and Docker-based local development.

## Current capabilities

- JSON and CSV input.
- Dynamic number of choices.
- Vietnamese prompts.
- Offline heuristic tests.
- Mock provider.
- Native Ollama provider.
- Optional OpenAI-compatible provider.
- Structured JSON output.
- CSV export.
- Debug logging.
- Benchmark summary.
- Docker local development workflow.
- Optional offline retrieval framework with local embeddings.

## Current exclusions

- No fine-tuning.
- No RAG.
- No embedding model.
- No reranker.
- No custom STEM solver.
- No GPU-specific optimization yet.
- No final competition Docker runtime decision yet.

## Project layout

```text
hackaithon-mcq-agent/
├── app/
├── data/
├── logs/
├── output/
├── scripts/
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── Makefile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Local setup

1. Create the virtualenv and install dependencies:

```bash
make install
```

2. Inspect the environment:

```bash
make inspect-env
```

3. Install and start Ollama locally. On macOS with Homebrew:

```bash
brew install --cask ollama
open -a Ollama
```

4. Pull the intended competition model:

```bash
ollama pull qwen3.5:9b
```

5. Run offline tests:

```bash
make test
```

6. Run the offline heuristic smoke test:

```bash
make run
```

7. Run a limited real-model smoke test:

```bash
make run-real-limit-3
```

The Ollama context window is configurable with `OLLAMA_NUM_CTX`. Larger values help long Vietnamese reading-comprehension items, but they increase memory usage and latency.

## Docker development setup

Build the local development image:

```bash
make docker-build
```

Run the offline smoke test in Docker:

```bash
make docker-run-offline
```

Run the real-model smoke test against Ollama on the host:

```bash
make docker-run-real
```

This container connects to a host Ollama service with `OLLAMA_BASE_URL=http://host.docker.internal:11434`. For Linux Docker hosts, include `--add-host=host.docker.internal:host-gateway`.

Important: this is a local development container. The final competition Docker packaging may need to bundle a different inference runtime or follow stricter organizer rules. Do not assume this image is already the final submission image.

## CLI

```bash
.venv/bin/python -m app.main --help
```

Example offline run:

```bash
.venv/bin/python -m app.main \
  --input ./data/sample_public_test.json \
  --output ./output/pred.csv \
  --solver-mode heuristic \
  --answer-format letter
```

Example real-model run:

```bash
.venv/bin/python -m app.main \
  --input ./data/sample_public_test.json \
  --output ./output/pred.csv \
  --solver-mode llm \
  --provider ollama \
  --answer-format letter \
  --limit 3
```

Example run with retrieval explicitly enabled:

```bash
.venv/bin/python -m app.main \
  --input ./data/sample_public_test.json \
  --output ./output/pred.csv \
  --solver-mode auto \
  --provider ollama \
  --retrieval on
```

## Evaluation workflow

The curated gold validation set is for evaluation only.
Do not fine-tune on it.
Human spot-check the labels before treating it as an official benchmark.

Run a limited gold evaluation:

```bash
make evaluate-gold-limit-10
```

Run the full gold evaluation:

```bash
make evaluate-gold
```

Run configured experiments on the first 10 gold questions:

```bash
make experiments-limit-10
```

Run all configured experiments:

```bash
make experiments
```

Export wrong, invalid, or fallback records for manual review:

```bash
make export-review EXPERIMENT=baseline_ctx_16384
```

Each evaluation run writes:

```text
reports/<experiment-name>/
├── summary.json
├── predictions.jsonl
├── errors.jsonl
├── category_metrics.json
└── report.md
```

The experiment runner also writes:

```text
reports/comparison.md
reports/comparison.json
```

## Inference strategy lab

The strategy lab benchmarks complete inference pipelines while keeping the rest of the production stack fixed.

- `baseline` runs the current production pipeline unchanged.
- `risk_second_pass` is a minimal proof-of-concept that can trigger one extra pass for static high-risk questions.
- Every strategy owns its full workflow and returns structured execution metadata.

Run the default baseline vs risk-second-pass comparison:

```bash
./.venv_bench/bin/python scripts/benchmark_strategies.py
```

Run one specific strategy:

```bash
./.venv_bench/bin/python scripts/benchmark_strategies.py \
  --strategy baseline
```

Useful knobs for the proof-of-concept risk strategy:

```bash
./.venv_bench/bin/python scripts/benchmark_strategies.py \
  --strategy risk_second_pass \
  --risk-threshold 0.75 \
  --second-pass-prompt-version compact \
  --keep-policy second
```

Artifacts are written to:

```text
reports/strategy_lab/<strategy>/
├── gold/
│   ├── summary.json
│   ├── predictions.jsonl
│   ├── errors.jsonl
│   ├── category_metrics.json
│   ├── metadata.json
│   └── report.md
└── public/
    ├── benchmark_summary.json
    ├── debug_predictions.jsonl
    ├── metadata.json
    └── summary.json

reports/strategy_lab/comparison.md
reports/strategy_lab/comparison.json
submissions/strategy_lab/<strategy>_submission.csv
```

## Retrieval framework

The retrieval layer is optional and disabled by default.

- `--retrieval off` preserves the current production behavior.
- `--retrieval on` enables a lightweight local retrieval step only for LLM-bound questions that pass a heuristic gate.
- Document embeddings are built offline and stored locally.
- Query embeddings are isolated behind a single interface so the embedding backend can be replaced later without changing the retrieval pipeline.

### Retrieval architecture

```text
question
-> heuristic solver (existing path)
-> if LLM is needed and retrieval=on:
   -> retrieval gate
   -> query embedding (local BGE-m3 interface)
   -> cosine top-k retrieval from precomputed vectors
   -> optional reranker if a local reranker becomes available
   -> short snippet injection into prompt
-> existing LLM generation path
```

Modules:

- `app/retrieval/loader.py`: loads KB docs and offline embedding index
- `app/retrieval/gate.py`: heuristic retrieval gating
- `app/retrieval/retriever.py`: cosine similarity and top-k retrieval
- `app/retrieval/context_builder.py`: snippet packing for prompt injection
- `app/retrieval/pipeline.py`: orchestration layer
- `app/reranker/`: optional reranker interface and fallback implementation

### Build the starter knowledge base

Generate the small curated corpus:

```bash
.venv/bin/python scripts/build_kb.py
```

This writes:

```text
knowledge_base/reference_documents.json
```

### Build offline BGE-m3 embeddings

Pull the local embedding model if needed:

```bash
ollama pull bge-m3
```

Build document embeddings offline:

```bash
.venv/bin/python scripts/build_embeddings.py
```

This writes:

```text
embeddings/bge_m3_reference_documents.json
```

Inference never regenerates document embeddings.

### Retrieval benchmark

Run the baseline, retrieval, and retrieval+rereanker-if-available comparison:

```bash
.venv/bin/python scripts/benchmark_retrieval.py
```

This writes:

```text
reports/retrieval_framework/
├── baseline/
├── retrieval_bge_m3/
├── retrieval_bge_m3_qwen_rerank/
├── comparison.md
└── summary.json
```

Note: the current reranker module is intentionally optional. If a compatible local Qwen reranker is unavailable, the benchmark keeps the cosine-only retrieval result and records the reranker variant as unavailable.

### Base model benchmark

Compare the current Qwen production baseline against one Gemma candidate without changing prompts, heuristics, parser, retrieval mode, or evaluation logic:

```bash
.venv_bench/bin/python scripts/benchmark_models.py \
  --reuse-baseline-artifacts \
  --candidate-model gemma4:e4b
```

This writes:

```text
reports/model_benchmark/
├── comparison.md
├── comparison.json
└── gemma4_e4b/
    ├── gold/
    └── public/
```

The Qwen baseline can be reused from the verified production artifacts so the experiment cost stays focused on the candidate model.

## Recommended optimization order

1. Measure baseline accuracy and latency.
2. Compare structured-output prompt variants.
3. Analyze errors by category.
4. Add category-specific optimizations only where metrics justify them.
5. Add deterministic STEM solvers only for well-defined patterns.
6. Build a separate fine-tuning dataset.
7. Fine-tune with LoRA or QLoRA only after the evaluation loop is stable.
8. Re-run Docker verification before submission.

## Competition TODO list

1. Will the private test input be JSON or CSV?
2. What is the required output representation for questions with more than four choices?
3. Which GPU will be used for official evaluation?
4. How much VRAM will be available?
5. Is the final Docker container allowed to access the Internet?
6. Is there a Docker image size limit?
7. Is there a total inference timeout?
8. May model weights be bundled into the image?
9. Will the organizer run the Docker image directly?
10. How many public leaderboard submissions are allowed?
11. Is an external inference endpoint forbidden during private evaluation?
12. Must all dependencies and model weights work fully offline?

## Next optimization steps

```text
baseline Ollama inference
-> benchmark accuracy and latency
-> prompt optimization
-> category-based routing
-> custom STEM solver if useful
-> quantization and batching
-> optional RAG only if external knowledge documents are provided
-> LoRA only if labeled training data becomes available
-> final offline competition Docker packaging
```
