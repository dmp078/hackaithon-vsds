from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os

from dotenv import load_dotenv


def default_output_root() -> Path:
    preferred = Path("/output")
    if preferred.exists():
        return preferred
    return Path("output")


def default_output_path(filename: str) -> Path:
    return default_output_root() / filename


@dataclass(slots=True)
class AppConfig:
    solver_mode: str = "heuristic"
    provider_name: str = "ollama"
    prompt_version: str = "baseline"
    answer_format: str = "letter"
    output_path: Path = field(default_factory=lambda: default_output_path("pred.csv"))
    debug_output_path: Path = field(default_factory=lambda: default_output_path("debug_predictions.jsonl"))
    benchmark_output_path: Path = field(default_factory=lambda: default_output_path("benchmark_summary.json"))
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:9b"
    ollama_timeout_seconds: float = 300.0
    ollama_num_ctx: int = 16384
    ollama_num_predict: int = 32
    ollama_temperature: float = 0.0
    ollama_think: bool = False
    openai_compatible_base_url: str = "http://localhost:8000/v1"
    openai_compatible_api_key: str = "dummy"
    openai_compatible_model: str = "qwen-placeholder"
    fallback_index: int = 0
    max_retries: int = 1
    log_level: str = "INFO"
    limit: int | None = None

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv()
        return cls(
            solver_mode=os.getenv("SOLVER_MODE", "heuristic"),
            provider_name=os.getenv("LLM_PROVIDER", "ollama"),
            prompt_version=os.getenv("PROMPT_VERSION", "baseline"),
            answer_format=os.getenv("ANSWER_FORMAT", "letter"),
            output_path=Path(os.getenv("OUTPUT_PATH", str(default_output_path("pred.csv")))),
            debug_output_path=Path(
                os.getenv("DEBUG_OUTPUT_PATH", str(default_output_path("debug_predictions.jsonl")))
            ),
            benchmark_output_path=Path(
                os.getenv("BENCHMARK_OUTPUT_PATH", str(default_output_path("benchmark_summary.json")))
            ),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "qwen3.5:9b"),
            ollama_timeout_seconds=float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300")),
            ollama_num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "16384")),
            ollama_num_predict=int(os.getenv("OLLAMA_NUM_PREDICT", "32")),
            ollama_temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0")),
            ollama_think=os.getenv("OLLAMA_THINK", "false").lower() == "true",
            openai_compatible_base_url=os.getenv(
                "OPENAI_COMPATIBLE_BASE_URL",
                "http://localhost:8000/v1",
            ),
            openai_compatible_api_key=os.getenv("OPENAI_COMPATIBLE_API_KEY", "dummy"),
            openai_compatible_model=os.getenv("OPENAI_COMPATIBLE_MODEL", "qwen-placeholder"),
            fallback_index=int(os.getenv("FALLBACK_INDEX", "0")),
            max_retries=int(os.getenv("MAX_RETRIES", "1")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def with_overrides(
        self,
        *,
        solver_mode: str | None = None,
        provider_name: str | None = None,
        answer_format: str | None = None,
        prompt_version: str | None = None,
        output_path: Path | None = None,
        log_level: str | None = None,
        limit: int | None = None,
    ) -> "AppConfig":
        return AppConfig(
            solver_mode=solver_mode or self.solver_mode,
            provider_name=provider_name or self.provider_name,
            prompt_version=prompt_version or self.prompt_version,
            answer_format=answer_format or self.answer_format,
            output_path=output_path or self.output_path,
            debug_output_path=(output_path.parent if output_path else self.debug_output_path.parent)
            / "debug_predictions.jsonl"
            if output_path
            else self.debug_output_path,
            benchmark_output_path=(output_path.parent if output_path else self.benchmark_output_path.parent)
            / "benchmark_summary.json"
            if output_path
            else self.benchmark_output_path,
            ollama_base_url=self.ollama_base_url,
            ollama_model=self.ollama_model,
            ollama_timeout_seconds=self.ollama_timeout_seconds,
            ollama_num_ctx=self.ollama_num_ctx,
            ollama_num_predict=self.ollama_num_predict,
            ollama_temperature=self.ollama_temperature,
            ollama_think=self.ollama_think,
            openai_compatible_base_url=self.openai_compatible_base_url,
            openai_compatible_api_key=self.openai_compatible_api_key,
            openai_compatible_model=self.openai_compatible_model,
            fallback_index=self.fallback_index,
            max_retries=self.max_retries,
            log_level=log_level or self.log_level,
            limit=limit,
        )
