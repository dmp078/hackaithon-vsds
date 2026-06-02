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
