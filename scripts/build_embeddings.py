from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import AppConfig
from app.retrieval.embedder import OllamaTextEmbedder
from app.retrieval.loader import load_knowledge_base


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build offline embeddings for the curated knowledge base")
    parser.add_argument("--input", type=Path, default=Path("knowledge_base/reference_documents.json"))
    parser.add_argument("--output", type=Path, default=Path("embeddings/bge_m3_reference_documents.json"))
    parser.add_argument("--model", default="bge-m3")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    documents = load_knowledge_base(args.input)
    config = AppConfig.from_env()
    embedder = OllamaTextEmbedder(config, model=args.model)
    records: list[dict[str, object]] = []
    dimension = 0

    for document in documents:
        text = "\n".join([document.title, ", ".join(document.keywords), document.content])
        vector = embedder.embed(text)
        dimension = len(vector)
        records.append({"id": document.id, "vector": vector})

    payload = {"model": args.model, "dimension": dimension, "records": records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload), encoding="utf-8")
    print(f"Wrote {len(records)} embeddings to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
