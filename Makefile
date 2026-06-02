PYTHON=.venv/bin/python
PIP=.venv/bin/pip

.PHONY: install test run run-limit-3 run-real run-real-limit-3 inspect-env docker-build docker-run-offline docker-run-real clean

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

clean:
	rm -f output/pred.csv output/public_smoke_pred.csv output/debug_predictions.jsonl output/benchmark_summary.json
