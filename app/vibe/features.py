"""Audio feature definitions, the LLM system prompt, and response parsing.

Pure module — no I/O, no global state. Easy to unit-test.
"""

import json

FEATURES = {
    "mood_happy":      {"range": (0.0, 1.0), "desc": "How happy/positive the music sounds"},
    "mood_sad":        {"range": (0.0, 1.0), "desc": "How melancholy/wistful"},
    "mood_relaxed":    {"range": (0.0, 1.0), "desc": "How calm/chill"},
    "mood_aggressive": {"range": (0.0, 1.0), "desc": "How intense/heavy"},
    "mood_party":      {"range": (0.0, 1.0), "desc": "How celebratory/festive"},
    "danceability":    {"range": (0.0, 1.0), "desc": "How groovy/danceable"},
    "energy":          {"range": (0.0, 1.0), "desc": "Overall loudness/intensity"},
    "arousal":         {"range": (0.0, 1.0), "desc": "Psychological activation level"},
    "valence":         {"range": (0.0, 1.0), "desc": "Psychological positivity"},
    "bpm":             {"range": (40.0, 220.0), "desc": "Tempo in beats per minute"},
}

VALID_FEATURES = set(FEATURES.keys())

# Not SQL — this .format() substitutes feature descriptions into a plain-text LLM prompt.
_SYSTEM_PROMPT = """You are a music curator AI. Given a scenario description, determine the ideal audio feature ranges for building a playlist. You must output ONLY valid JSON.

Available audio features and their ranges:
{features}

Rules:
- Only include features that are relevant to the scenario. Omitted features will not be filtered.
- Each feature value must be a [min, max] array.
- For 0-1 features, values must be between 0.0 and 1.0.
- For bpm, values must be between 40 and 220.
- Include a short "reasoning" string explaining your choices.

Output format:
{{"ranges": {{"feature_name": [min, max], ...}}, "reasoning": "one sentence"}}"""


def build_system_prompt() -> str:
    lines = []
    for name, info in FEATURES.items():
        lo, hi = info["range"]
        lines.append(f"- {name} ({lo}-{hi}): {info['desc']}")
    return _SYSTEM_PROMPT.format(features="\n".join(lines))  # safe: no SQL


def parse_llm_response(raw_text: str):
    """Extract and validate JSON {ranges, reasoning} from LLM output.

    Returns (ranges: dict[str, [lo, hi]], reasoning: str).
    Raises ValueError if no JSON or no valid ranges are present.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        kept = [ln for ln in text.split("\n") if not ln.strip().startswith("```")]
        text = "\n".join(kept).strip()

    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in LLM response: {text[:200]}")

    data = json.loads(text[start:end])
    raw_ranges = data.get("ranges", {})
    reasoning = data.get("reasoning", "")

    validated = {}
    for feature, bounds in raw_ranges.items():
        if feature not in VALID_FEATURES:
            continue
        if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
            continue
        try:
            lo, hi = float(bounds[0]), float(bounds[1])
        except (TypeError, ValueError):
            continue
        feat_lo, feat_hi = FEATURES[feature]["range"]
        lo = max(feat_lo, min(feat_hi, lo))
        hi = max(feat_lo, min(feat_hi, hi))
        if lo > hi:
            lo, hi = hi, lo
        validated[feature] = [lo, hi]

    if not validated:
        raise ValueError("LLM returned no valid feature ranges")
    return validated, reasoning
