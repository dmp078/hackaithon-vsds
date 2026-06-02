#!/usr/bin/env bash
set -euo pipefail

docker build -t hackaithon-mcq-agent:dev .
docker run --rm \
  -v "$(pwd)/data:/data" \
  -v "$(pwd)/output:/output" \
  hackaithon-mcq-agent:dev \
  --input /data/sample_public_test.json \
  --output /output/pred.csv \
  --solver-mode heuristic \
  --answer-format letter

if [[ "${1:-}" == "--real" ]]; then
  docker run --rm \
    --add-host=host.docker.internal:host-gateway \
    -e SOLVER_MODE=llm \
    -e LLM_PROVIDER=ollama \
    -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    -e OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3.5:9b}" \
    -v "$(pwd)/data:/data" \
    -v "$(pwd)/output:/output" \
    hackaithon-mcq-agent:dev \
    --input /data/sample_public_test.json \
    --output /output/pred.csv \
    --solver-mode llm \
    --provider ollama \
    --limit 3
fi
