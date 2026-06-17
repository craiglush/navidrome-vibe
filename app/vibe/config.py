"""Environment-driven configuration. No secrets are hard-coded."""

import os
from dataclasses import dataclass


def _bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Config:
    # Subsonic / Navidrome
    navidrome_url: str
    navidrome_user: str
    navidrome_password: str
    # Databases
    analysis_db_path: str
    vibe_db_path: str
    # LLM
    llm_provider: str
    ollama_url: str
    ollama_model: str
    ollama_think: bool
    ollama_num_ctx: int
    openai_base_url: str
    openai_api_key: str
    openai_model: str
    anthropic_api_key: str
    anthropic_model: str
    # App
    api_token: str
    port: int

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            navidrome_url=os.environ.get("NAVIDROME_URL", "http://navidrome:4533").rstrip("/"),
            navidrome_user=os.environ.get("NAVIDROME_USER", "admin"),
            navidrome_password=os.environ.get("NAVIDROME_PASSWORD", ""),
            analysis_db_path=os.environ.get("ANALYSIS_DB_PATH", "/data/analysis.db"),
            vibe_db_path=os.environ.get("VIBE_DB_PATH", "/data/vibe.db"),
            llm_provider=os.environ.get("VIBE_LLM_PROVIDER", "ollama").strip().lower(),
            ollama_url=os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434").rstrip("/"),
            ollama_model=os.environ.get("OLLAMA_MODEL", "qwen2.5:7b"),
            ollama_think=_bool("OLLAMA_THINK", False),
            ollama_num_ctx=int(os.environ.get("OLLAMA_NUM_CTX", "8192")),
            openai_base_url=os.environ.get("OPENAI_BASE_URL", "").rstrip("/"),
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            openai_model=os.environ.get("OPENAI_MODEL", ""),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            anthropic_model=os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5"),
            api_token=os.environ.get("VIBE_API_TOKEN", ""),
            port=int(os.environ.get("VIBE_PORT", "4546")),
        )
