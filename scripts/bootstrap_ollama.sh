#!/usr/bin/env bash
set -euo pipefail

MODEL="${OLLAMA_MODEL:-qwen3.5:9b}"
BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"

if ! command -v ollama >/dev/null 2>&1; then
  case "$(uname -s)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        echo "Ollama is missing. Install with: brew install --cask ollama"
      else
        echo "Ollama is missing. Install Homebrew first, then run: brew install --cask ollama"
      fi
      ;;
    Linux)
      echo "Ollama is missing. Install with: curl -fsSL https://ollama.com/install.sh | sh"
      ;;
    MINGW*|MSYS*|CYGWIN*)
      echo "Ollama is missing. Install with: irm https://ollama.com/install.ps1 | iex"
      ;;
    *)
      echo "Unsupported OS for automatic Ollama bootstrap"
      ;;
  esac
  exit 1
fi

if ! curl --fail --silent "${BASE_URL}/api/tags" >/dev/null; then
  mkdir -p logs
  nohup ollama serve > logs/ollama.log 2>&1 &
  sleep 5
fi

curl --fail --silent "${BASE_URL}/api/tags" >/dev/null
ollama pull "${MODEL}"
ollama run "${MODEL}" "Return only the word OK."
curl --fail --silent "${BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${MODEL}\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Choose the correct answer. Question: 2 + 2 = ? Choices: [0] 3 [1] 4 [2] 5. Return JSON only with selected_index.\"}],
    \"stream\": false,
    \"think\": false,
    \"format\": {
      \"type\": \"object\",
      \"properties\": {\"selected_index\": {\"type\": \"integer\", \"minimum\": 0, \"maximum\": 2}},
      \"required\": [\"selected_index\"]
    },
    \"options\": {\"temperature\": 0, \"num_predict\": 16}
  }"
