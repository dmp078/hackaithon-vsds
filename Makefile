PYTHON=.venv/bin/python
PIP=.venv/bin/pip
MODEL ?= qwen3.5:9b

.PHONY: install test run run-limit-3 run-real run-real-limit-3 inspect-env docker-build docker-run-offline docker-run-real evaluate-gold-limit-10 evaluate-gold experiments-limit-10 experiments export-review clean

install:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m pytest

run:
	$(PYTHON) -m app.main --input ./data/sample_public_test.json --output ./output/pred.csv --solver-mode heuristic --answer-format letter

run-limit-3:
	$(PYTHON) -m app.main --input ./data/sample_public_test.json --output ./output/pred.csv --solver-mode heuristic --answer-format letter --limit 3

run-real:
	$(PYTHON) -m app.main --input ./data/sample_public_test.json --output ./output/pred.csv --solver-mode llm --provider ollama --answer-format letter

run-real-limit-3:
	$(PYTHON) -m app.main --input ./data/sample_public_test.json --output ./output/pred.csv --solver-mode llm --provider ollama --answer-format letter --limit 3

inspect-env:
	./scripts/inspect_environment.sh

docker-build:
	docker build -t hackaithon-mcq-agent:dev .

docker-run-offline:
	./scripts/docker_smoke_test.sh

docker-run-real:
	./scripts/docker_smoke_test.sh --real

evaluate-gold-limit-10:
	$(PYTHON) scripts/evaluate_gold.py --input data/gold_validation.json --provider ollama --model $(MODEL) --prompt-version baseline --output-dir reports/baseline_limit_10 --limit 10

evaluate-gold:
	$(PYTHON) scripts/evaluate_gold.py --input data/gold_validation.json --provider ollama --model $(MODEL) --prompt-version baseline --output-dir reports/baseline

experiments-limit-10:
	$(PYTHON) scripts/run_experiments.py --config experiments/experiments.yaml --input data/gold_validation.json --provider ollama --model $(MODEL) --limit 10

experiments:
	$(PYTHON) scripts/run_experiments.py --config experiments/experiments.yaml --input data/gold_validation.json --provider ollama --model $(MODEL)

export-review:
	$(PYTHON) scripts/export_review_sheet.py --experiment $(EXPERIMENT)

clean:
	rm -f output/pred.csv output/public_smoke_pred.csv output/debug_predictions.jsonl output/benchmark_summary.json
