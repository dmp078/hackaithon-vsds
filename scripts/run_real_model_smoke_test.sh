#!/usr/bin/env bash
set -euo pipefail

.venv/bin/python -m app.main \
  --input ./data/sample_public_test.json \
  --output ./output/pred.csv \
  --solver-mode llm \
  --provider ollama \
  --answer-format letter \
  --limit 3
