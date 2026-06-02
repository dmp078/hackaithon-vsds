#!/usr/bin/env bash
set -euo pipefail

uname -a
python3 --version
which python3
which ollama || true
ollama --version || true
docker --version || true
nvidia-smi || true
system_profiler SPHardwareDataType || true
free -h || true
df -h .
