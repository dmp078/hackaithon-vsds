# Inference Strategy Lab Design

## Goal

Build a lightweight experimental framework that benchmarks complete inference pipelines as interchangeable strategies while keeping the existing production pipeline intact.

## Strategy boundary

Each strategy owns one complete inference workflow:

`question -> strategy pipeline -> final answer + execution metadata`

The benchmark runner does not know how the strategy works internally. It only calls:

`strategy.execute(question, context) -> StrategyResult`

## Initial scope

Implement only:

- `baseline`
- `risk_second_pass`

Do not implement other strategy types in this phase.

## StrategyResult

Each strategy returns:

- `final_prediction`
- `total_llm_calls`
- `triggered`
- `metadata`
- `intermediate_predictions`

The final prediction latency is the total end-to-end strategy latency for that question.

## Benchmark scope

Support both:

- gold evaluation
- public submission generation

Gold metrics:

- accuracy
- invalid output rate
- fallback rate
- average latency
- p95 latency

Public metrics:

- submission artifact
- disagreement vs production baseline
- average latency
- p95 latency
- total llm calls
- trigger rate
- metadata.json with exact configuration

## Design choice

Reuse current providers, solvers, parser, heuristics, and retrieval settings.

The new strategy layer wraps existing production behavior instead of replacing it.

## Risk second pass

The proof-of-concept strategy uses:

- static question-level risk scoring
- one optional second pass
- configurable second-pass prompt version
- configurable keep policy

No threshold tuning or prompt optimization is part of this phase.
