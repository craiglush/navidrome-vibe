import pytest
from vibe.features import build_system_prompt, parse_llm_response, VALID_FEATURES


def test_system_prompt_lists_features():
    p = build_system_prompt()
    assert "mood_happy" in p
    assert "bpm" in p
    assert "JSON" in p


def test_parse_valid_json():
    raw = '{"ranges": {"mood_relaxed": [0.5, 1.0], "energy": [0.0, 0.2]}, "reasoning": "calm"}'
    ranges, reasoning = parse_llm_response(raw)
    assert ranges == {"mood_relaxed": [0.5, 1.0], "energy": [0.0, 0.2]}
    assert reasoning == "calm"


def test_parse_strips_code_fences():
    raw = '```json\n{"ranges": {"bpm": [120, 140]}, "reasoning": "x"}\n```'
    ranges, _ = parse_llm_response(raw)
    assert ranges == {"bpm": [120.0, 140.0]}


def test_parse_clamps_and_orders():
    raw = '{"ranges": {"mood_happy": [1.4, -0.2]}, "reasoning": ""}'
    ranges, _ = parse_llm_response(raw)
    assert ranges == {"mood_happy": [0.0, 1.0]}


def test_parse_drops_unknown_features():
    raw = '{"ranges": {"nonsense": [0, 1], "energy": [0.1, 0.3]}, "reasoning": ""}'
    ranges, _ = parse_llm_response(raw)
    assert ranges == {"energy": [0.1, 0.3]}
    assert "nonsense" not in VALID_FEATURES


def test_parse_no_json_raises():
    with pytest.raises(ValueError):
        parse_llm_response("I am not JSON at all")


def test_parse_empty_ranges_raises():
    with pytest.raises(ValueError):
        parse_llm_response('{"ranges": {}, "reasoning": "nothing"}')
