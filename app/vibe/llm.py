"""Pluggable LLM access. Default provider is local Ollama; OpenAI-compatible
and Anthropic are optional. The qwen 'thinking' workaround (think/num_ctx) is
now config-driven, not hard-coded.
"""

import logging

import requests

from vibe.features import build_system_prompt

log = logging.getLogger(__name__)

_USER_PROMPT = 'Scenario: "{scenario}"'
_TITLE_SYSTEM = (
    "You are a playlist naming assistant. Given a description of a playlist, "
    "generate a short, catchy playlist title (2-5 words). No quotes, no emoji, "
    "no punctuation except hyphens. Just the title, nothing else."
)


def _ollama(system_prompt, user_prompt, cfg):
    payload = {
        "model": cfg.ollama_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "think": cfg.ollama_think,
        "options": {"temperature": 0.3, "num_ctx": cfg.ollama_num_ctx},
    }
    url = cfg.ollama_url + "/api/chat"  # safe: URL construction, not SQL
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _anthropic(system_prompt, user_prompt, cfg):
    if not cfg.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not configured")
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": cfg.anthropic_api_key,
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={"model": cfg.anthropic_model, "max_tokens": 512,
              "system": system_prompt,
              "messages": [{"role": "user", "content": user_prompt}],
              "temperature": 0.3},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def _openai(system_prompt, user_prompt, cfg):
    if not cfg.openai_base_url:
        raise RuntimeError("OPENAI_BASE_URL not configured")
    headers = {"Content-type": "application/json"}
    if cfg.openai_api_key:
        headers["Authorization"] = "Bearer " + cfg.openai_api_key
    url = cfg.openai_base_url + "/api/v1/chat/completions"  # safe: URL construction, not SQL
    resp = requests.post(
        url,
        headers=headers,
        json={"model": cfg.openai_model,
              "messages": [{"role": "system", "content": system_prompt},
                           {"role": "user", "content": user_prompt}],
              "temperature": 0.3},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _dispatch(system_prompt, user_prompt, cfg):
    if cfg.llm_provider == "anthropic":
        return _anthropic(system_prompt, user_prompt, cfg)
    if cfg.llm_provider == "openai":
        return _openai(system_prompt, user_prompt, cfg)
    return _ollama(system_prompt, user_prompt, cfg)  # default: ollama


def interpret_scenario(scenario: str, cfg) -> str:
    """Return the LLM's raw text response for a scenario (caller parses JSON)."""
    return _dispatch(build_system_prompt(), _USER_PROMPT.format(scenario=scenario), cfg)


def generate_title(description: str, cfg) -> str:
    """Short playlist title from a description; falls back to the description."""
    try:
        raw = _dispatch(_TITLE_SYSTEM, description, cfg)
        title = raw.strip().strip('"\'').strip()
        if not title or len(title) > 60:
            return description[:60].strip()
        return title
    except Exception as e:
        log.warning("Title generation failed, using description: %s", e)
        return description[:60].strip()
