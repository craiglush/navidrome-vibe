import os
from vibe.config import Config


def test_from_env_defaults(monkeypatch):
    for k in ("VIBE_LLM_PROVIDER", "OLLAMA_MODEL", "NAVIDROME_USER"):
        monkeypatch.delenv(k, raising=False)
    cfg = Config.from_env()
    assert cfg.llm_provider == "ollama"
    assert cfg.ollama_model == "qwen2.5:7b"
    assert cfg.navidrome_user == "admin"
    assert cfg.ollama_think is False


def test_from_env_overrides(monkeypatch):
    monkeypatch.setenv("VIBE_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("OLLAMA_THINK", "true")
    monkeypatch.setenv("NAVIDROME_PASSWORD", "secret")
    cfg = Config.from_env()
    assert cfg.llm_provider == "anthropic"
    assert cfg.ollama_think is True
    assert cfg.navidrome_password == "secret"
