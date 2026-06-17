import responses
from vibe.llm import interpret_scenario, generate_title


@responses.activate
def test_ollama_default_uses_native_chat(cfg):
    responses.add(
        responses.POST, "http://ollama.test/api/chat",
        json={"message": {"content": '{"ranges": {"energy": [0.0,0.2]}, "reasoning": "calm"}'}},
        status=200,
    )
    out = interpret_scenario("quiet night", cfg)
    assert "energy" in out
    body = responses.calls[0].request.body.decode()
    assert '"think": false' in body
    assert '"num_ctx": 8192' in body


@responses.activate
def test_anthropic_provider(cfg):
    cfg.llm_provider = "anthropic"
    responses.add(
        responses.POST, "https://api.anthropic.com/v1/messages",
        json={"content": [{"text": '{"ranges": {"bpm": [120,140]}, "reasoning": "x"}'}]},
        status=200,
    )
    out = interpret_scenario("workout", cfg)
    assert "bpm" in out


@responses.activate
def test_openai_compatible_provider(cfg):
    cfg.llm_provider = "openai"
    responses.add(
        responses.POST, "http://owui.test/api/v1/chat/completions",
        json={"choices": [{"message": {"content": '{"ranges": {"mood_happy":[0.6,1.0]}}'}}]},
        status=200,
    )
    out = interpret_scenario("sunny", cfg)
    assert "mood_happy" in out


@responses.activate
def test_generate_title_strips_quotes(cfg):
    responses.add(
        responses.POST, "http://ollama.test/api/chat",
        json={"message": {"content": '  "Rainy Day Calm"  '}},
        status=200,
    )
    assert generate_title("rainy", cfg) == "Rainy Day Calm"


@responses.activate
def test_generate_title_falls_back_on_error(cfg):
    responses.add(responses.POST, "http://ollama.test/api/chat", status=500)
    assert generate_title("a lazy sunday morning with coffee", cfg).startswith("a lazy sunday")
