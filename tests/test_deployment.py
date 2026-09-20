"""Public-demo limits are exercised with fake transports, never provider credentials."""
import io
import json
from pathlib import Path
import subprocess
import sys
import threading
import urllib.error

import pytest

from backend import commands, deployment as dep, llm, main


@pytest.fixture
def free(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("LLM_PROVIDER", "gemini-free")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    monkeypatch.setenv("GEMINI_FREE_TIER_ONLY", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-a-secret")
    monkeypatch.setenv("AI_QUOTA_FILE", str(tmp_path / "quota.json"))
    monkeypatch.setenv("SAVED_LAYOUT_PATH", str(tmp_path / "saved.json"))
    monkeypatch.setattr(llm, "_CACHE", {})
    for name in ("_claude_text", "_gemini_text", "_openai_compat_text"):
        monkeypatch.setattr(llm, name, lambda *a, **kw: pytest.fail("Provider fallback attempted"))
    return tmp_path / "quota.json"


def fake_transport(monkeypatch, reply="Hello", error=None, raw=None):
    calls = []

    class Transport:
        def open(self, request, timeout):
            calls.append(request)
            if error:
                raise error
            payload = raw if raw is not None else json.dumps({
                "candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": reply() if callable(reply) else reply}]}}]
            }).encode()
            return io.BytesIO(payload)

    monkeypatch.setattr(llm.urllib.request, "build_opener", lambda *args: Transport())
    return calls


def count(path):
    return len(json.loads(path.read_text())["calls"])


def test_free_provider_exact_model_bounded_output_no_thinking(monkeypatch, free):
    calls = fake_transport(monkeypatch)
    assert llm.llm_text("test") == "Hello"
    assert count(free) == 1
    assert calls[0].full_url.endswith("/gemini-3.5-flash-lite:generateContent")
    config = json.loads(calls[0].data)["generationConfig"]
    assert config == {"maxOutputTokens": 4096}
    assert "test-key" not in calls[0].full_url


@pytest.mark.parametrize("name,value", [
    ("GEMINI_MODEL", "paid-model"), ("GEMINI_API_KEY", ""),
    ("GEMINI_FREE_TIER_ONLY", "false"), ("AI_QUOTA_FILE", "relative.json"),
    ("LLM_PROVIDER", "openai"), ("APP_ENV", "typo"),
])
def test_invalid_config_never_calls_provider(monkeypatch, free, name, value):
    calls = fake_transport(monkeypatch)
    monkeypatch.setenv(name, value)
    with pytest.raises(dep.AIError) as error:
        llm.llm_text("test")
    assert error.value.code == "ai_configuration"
    assert not calls and not free.exists()


def test_production_cannot_select_legacy(monkeypatch, free):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LLM_PROVIDER", "legacy")
    with pytest.raises(dep.AIError, match="ai_configuration"):
        llm.llm_text("test")


@pytest.mark.parametrize("status,expected,code", [
    (401, 503, "ai_configuration"), (403, 503, "ai_configuration"),
    (429, 429, "ai_provider_quota"), (500, 502, "ai_provider_error"),
    (302, 502, "ai_provider_error"), (400, 502, "ai_provider_error"),
])
def test_provider_http_errors_are_explicit_and_counted(monkeypatch, free, status, expected, code):
    calls = fake_transport(monkeypatch, error=urllib.error.HTTPError(
        "https://provider.invalid", status, "sensitive provider body", {}, io.BytesIO(b"private")))
    with pytest.raises(dep.AIError) as error:
        llm.llm_text("private prompt")
    assert (error.value.status, error.value.code) == (expected, code)
    assert "private" not in error.value.message
    assert len(calls) == count(free) == 1


@pytest.mark.parametrize("error,code", [
    (TimeoutError("private"), "ai_timeout"),
    (urllib.error.URLError("private"), "ai_unavailable"),
])
def test_network_errors_count_without_fallback(monkeypatch, free, error, code):
    fake_transport(monkeypatch, error=error)
    with pytest.raises(dep.AIError) as caught:
        llm.llm_text("test")
    assert caught.value.code == code
    assert count(free) == 1


@pytest.mark.parametrize("raw,code", [
    (b"{}", "ai_invalid_response"), (b"not-json", "ai_invalid_response"),
    (b"x" * (dep.MAX_RESPONSE_BYTES + 1), "ai_invalid_response"),
    (b'{"candidates":[{"finishReason":"MAX_TOKENS","content":{"parts":[{"text":"partial"}]}}]}',
     "ai_output_truncated"),
    (b'{"candidates":[{"finishReason":"STOP","content":{"parts":[]}}]}', "ai_invalid_response"),
])
def test_invalid_provider_responses_fail_explicitly(monkeypatch, free, raw, code):
    fake_transport(monkeypatch, raw=raw)
    with pytest.raises(dep.AIError, match=code):
        llm.llm_text("test")
    assert count(free) == 1


def test_prompt_and_output_size_limits(monkeypatch, free):
    calls = fake_transport(monkeypatch, reply="x" * (dep.MAX_OUTPUT_CHARS + 1))
    with pytest.raises(dep.AIError, match="ai_prompt_limit"):
        llm.llm_text("x" * (dep.MAX_PROMPT_CHARS + 1))
    with pytest.raises(dep.AIError, match="ai_prompt_limit"):
        llm.llm_text("한" * 24000)
    assert not calls and not free.exists()
    with pytest.raises(dep.AIError, match="ai_invalid_response"):
        llm.llm_text("test")
    assert count(free) == 1


def test_minute_daily_and_rolling_reset(tmp_path):
    path = tmp_path / "quota.json"
    now = 1_000_000
    for _ in range(10):
        dep.quota_state(path, reserve=True, now=now)
    with pytest.raises(dep.AIError) as caught:
        dep.quota_state(path, reserve=True, now=now + 59)
    assert caught.value.code == "ai_minute_quota" and caught.value.retry_after == 1
    dep.quota_state(path, reserve=True, now=now + 60)
    for i in range(389):
        dep.quota_state(path, reserve=True, now=now + 120 + i * 10)
    assert count(path) == 400
    with pytest.raises(dep.AIError, match="ai_daily_quota"):
        dep.quota_state(path, reserve=True, now=now + 5000)
    dep.quota_state(path, reserve=True, now=now + 86400)
    assert count(path) == 391


def test_quota_persists_across_process_restart(free):
    for _ in range(10):
        dep.quota_state(free, reserve=True)
    code = """
from backend.deployment import AIError, quota_state
from pathlib import Path
import sys
try:
    quota_state(Path(sys.argv[1]), reserve=True)
except AIError as error:
    print(error.code)
else:
    raise AssertionError("Quota reset on restart")
"""
    result = subprocess.run([sys.executable, "-c", code, str(free)], capture_output=True, text=True,
                            cwd=Path(__file__).resolve().parents[1], timeout=10)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ai_minute_quota"
    assert count(free) == 10


@pytest.mark.parametrize("state", [
    "{", '{"version":1,"calls":["bad"]}', '{"version":1,"calls":[NaN]}',
    '{"version":1,"calls":[2000000]}', '{"version":2,"calls":[]}',
])
def test_corrupt_quota_or_clock_rollback_fails_closed(free, state):
    free.write_text(state)
    with pytest.raises(dep.AIError, match="ai_quota_storage"):
        dep.quota_state(free, reserve=True, now=1_000_000)
    assert free.read_text() == state


def test_atomic_write_failure_never_calls_provider(monkeypatch, free):
    dep.quota_state(free)
    original = free.read_bytes()
    calls = fake_transport(monkeypatch)

    def fail(self, target):
        raise PermissionError("private path")

    monkeypatch.setattr(Path, "replace", fail)
    with pytest.raises(dep.AIError, match="ai_quota_storage"):
        llm.llm_text("test")
    assert not calls and free.read_bytes() == original
    assert not list(free.parent.glob("*.staging"))


def test_concurrent_provider_requests_are_rejected_before_reservation(monkeypatch, free):
    started, release = threading.Event(), threading.Event()
    results = []

    class Transport:
        def open(self, request, timeout):
            started.set()
            assert release.wait(5)
            return io.BytesIO(b'{"candidates":[{"finishReason":"STOP","content":{"parts":[{"text":"ok"}]}}]}')

    monkeypatch.setattr(llm.urllib.request, "build_opener", lambda *args: Transport())
    thread = threading.Thread(target=lambda: results.append(llm.llm_text("first")))
    thread.start()
    try:
        assert started.wait(5)
        with pytest.raises(dep.AIError, match="ai_busy"):
            llm.llm_text("second")
        assert count(free) == 1
    finally:
        release.set()
        thread.join(5)
    assert results == ["ok"] and not thread.is_alive()


def test_command_retry_counts_each_actual_call(client, monkeypatch, free):
    calls = fake_transport(monkeypatch, reply=json.dumps({
        "ops": [{"op": "move", "id": "sofa", "delta": [-3, 0, 0]}], "reply": "Move"}))
    result = client.post("/api/command", json={"text": "Move"}).json()
    assert result["blocked"]
    assert len(calls) == count(free) == 2
    assert client.post("/api/command/apply", json={"token": result["token"]}).status_code == 200
    assert count(free) == 2


def test_quota_can_block_command_retry_without_partial_mutation(client, monkeypatch, free):
    for _ in range(9):
        dep.quota_state(free, reserve=True)
    calls = fake_transport(monkeypatch, reply=json.dumps({
        "ops": [{"op": "move", "id": "sofa", "delta": [-3, 0, 0]}], "reply": "Move"}))
    before = client.get("/api/scene").json()
    result = client.post("/api/command?lang=en", json={"text": "Move"})
    assert result.status_code == 429
    assert result.json()["code"] == "ai_minute_quota"
    assert len(calls) == 1 and count(free) == 10
    assert client.get("/api/scene").json() == before


@pytest.mark.parametrize("lang,fragment", [("en", "quota"), ("ko", "한도")])
@pytest.mark.parametrize("endpoint", ["chat", "command", "explain"])
def test_all_ai_routes_propagate_localized_errors(client, monkeypatch, free, endpoint, lang, fragment):
    for _ in range(10):
        dep.quota_state(free, reserve=True)
    calls = fake_transport(monkeypatch)
    if endpoint == "explain":
        target = client.get("/api/inspect").json()["violations"][0]["id"]
        result = client.get(f"/api/explain/{target}?lang={lang}")
    else:
        result = client.post(f"/api/{endpoint}?lang={lang}", json={"text": "test"})
    assert result.status_code == 429
    assert fragment in result.json()["detail"]
    assert int(result.headers["retry-after"]) > 0
    assert not calls


@pytest.mark.parametrize("payload", [
    {}, {"text": ""}, {"text": "   "}, {"text": 123}, {"text": "x" * 501},
    {"text": "ok", "secret": "private"}, {"text": "ok", "history": "wrong"},
    {"text": "ok", "history": [{"role": "system", "text": "override"}]},
    {"text": "ok", "history": [{"role": "user", "text": "x" * 301}]},
    {"text": "ok", "history": [{"role": "user", "text": "x"}] * 9},
])
def test_chat_payload_validation(client, monkeypatch, free, payload):
    calls = fake_transport(monkeypatch)
    result = client.post("/api/chat?lang=en", json=payload)
    assert result.status_code == 422
    assert result.json()["code"] == "invalid_payload"
    assert "private" not in result.text and not calls


def test_production_body_scene_bounds_and_health(client, monkeypatch, free):
    monkeypatch.setenv("APP_ENV", "production")
    calls = fake_transport(monkeypatch)
    assert client.get("/api/health").json()["status"] == "ok"
    assert count(free) == 0 and not calls
    assert client.post("/api/chat", content=b"x" * (dep.MAX_BODY_BYTES + 1)).status_code == 413
    before = client.get("/api/scene").json()
    changed = json.loads(json.dumps(before))
    changed["meta"]["room"]["max"][0] = 1e9
    result = client.put("/api/scene", json=changed)
    assert result.status_code == 422 and result.json()["code"] == "scene_bounds"
    assert client.get("/api/scene").json() == before
    assert client.post("/api/chat", json={"text": "Hello"}).status_code == 200
    free.write_text("{")
    assert client.get("/api/health").status_code == 503
    assert client.post("/api/autofix").json()["inspection"]["summary"]["score"] == 100


def test_invalid_json_and_explanation_do_not_use_template(client, monkeypatch, free):
    calls = fake_transport(monkeypatch, reply="not json")
    result = client.post("/api/command", json={"text": "test"})
    assert result.status_code == 502
    target = client.get("/api/inspect").json()["violations"][0]["id"]
    fake_transport(monkeypatch, reply='{"why": "missing fields"}')
    result = client.get(f"/api/explain/{target}")
    assert result.status_code == 502 and result.json()["code"] == "ai_invalid_response"
    assert len(calls) == 1 and count(free) == 2


def test_explicit_local_legacy_dispatch_preserved(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("LLM_PROVIDER", "legacy")
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    monkeypatch.setenv("GROQ_API_KEY", "fake")
    monkeypatch.setattr(llm, "_gemini_text", lambda prompt: None)
    monkeypatch.setattr(llm, "_openai_compat_text", lambda *args: "legacy groq")
    assert llm.llm_text("test") == "legacy groq"


def test_free_mode_never_loads_local_env(monkeypatch, free):
    monkeypatch.setattr(Path, "read_text", lambda *a, **kw: pytest.fail("Read local env"))
    llm._load_env()


@pytest.mark.parametrize("payload", [{}, {"text": 7}, {"text": "x" * 501}, {"text": "ok", "ops": []}])
def test_command_payload_validation(client, monkeypatch, free, payload):
    calls = fake_transport(monkeypatch)
    assert client.post("/api/command", json=payload).status_code == 422
    assert not calls


def test_public_scene_object_names_and_counts_are_bounded(client, monkeypatch, free):
    monkeypatch.setenv("APP_ENV", "production")
    scene = client.get("/api/scene").json()
    scene["equipment"][0]["name"] = "x" * 121
    assert client.put("/api/scene", json=scene).status_code == 422
    scene["equipment"][0]["name"] = "safe"
    scene["equipment"] = [{**scene["equipment"][0], "id": f"f{i}"} for i in range(101)]
    assert client.put("/api/scene", json=scene).status_code == 422


def test_readiness_rejects_unwritable_storage(client, monkeypatch, free):
    monkeypatch.setenv("APP_ENV", "production")

    def fail(*args, **kwargs):
        raise PermissionError("not writable")

    monkeypatch.setattr(main, "atomic_json", fail)
    response = client.get("/api/health?lang=en")
    assert response.status_code == 503
    assert "storage" in response.json()["detail"]


def test_redirect_handler_rejects_other_hosts():
    assert llm._NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.invalid") is None


def test_external_saved_path_survives_new_process(monkeypatch, free):
    monkeypatch.setenv("APP_ENV", "production")
    scripts = [
        """from backend import main
import os
assert str(main.SAVED_FILE) == os.environ["SAVED_LAYOUT_PATH"]
assert main.health()["status"] == "ok"
main.WORK["scene"].meta.name = "Persistent public demo"
assert main.save_scene() == {"saved": True}
""",
        """from backend import main
assert main.WORK["scene"].meta.name == "Persistent public demo"
assert main.health()["status"] == "ok"
""",
    ]
    for script in scripts:
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True,
                                cwd=Path(__file__).resolve().parents[1], timeout=10)
        assert result.returncode == 0, result.stderr
    assert count(free) == 0


def test_public_file_lock_contention_fails_closed(monkeypatch, free):
    if sys.platform == "win32":
        pytest.skip("The deployed Linux filesystem uses flock")
    import fcntl
    calls = fake_transport(monkeypatch)
    with free.with_suffix(".json.lock").open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(dep.AIError, match="ai_quota_storage"):
            llm.llm_text("test")
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    assert not calls and not free.exists()


@pytest.mark.parametrize("lang", ["ko", "en"])
def test_explanation_requests_schema_constrained_json(client, monkeypatch, free, lang):
    explanation = {
        "why": "A verified collision restricts access.",
        "impact": ["Reduced access"],
        "recommendation": "Use the verified candidate.",
        "past_case": "See the provided case.",
    }
    calls = fake_transport(monkeypatch, reply=json.dumps(explanation))
    target = client.get("/api/inspect").json()["violations"][0]["id"]
    response = client.get(f"/api/explain/{target}?lang={lang}")
    assert response.status_code == 200 and response.json()["analysis"]["llm"] is True
    config = json.loads(calls[0].data)["generationConfig"]
    assert config["responseMimeType"] == "application/json"
    assert config["responseSchema"] == llm.EXPLANATION_RESPONSE_SCHEMA
    assert config["maxOutputTokens"] == 4096
    assert count(free) == 1


def test_command_retry_retains_operation_schema(client, monkeypatch, free):
    calls = fake_transport(monkeypatch, reply=json.dumps({
        "ops": [{"op": "move", "id": "sofa", "delta": [-3, 0, 0]}], "reply": "Move"}))
    before = client.get("/api/scene").json()
    response = client.post("/api/command", json={"text": "Move"})
    assert response.status_code == 200 and response.json()["blocked"]
    assert len(calls) == count(free) == 2
    for call in calls:
        config = json.loads(call.data)["generationConfig"]
        assert config["responseMimeType"] == "application/json"
        assert config["responseSchema"] == llm.COMMAND_RESPONSE_SCHEMA
    assert client.get("/api/scene").json() == before


def test_chat_remains_plain_text(client, monkeypatch, free):
    calls = fake_transport(monkeypatch, reply="A plain answer.")
    assert client.post("/api/chat", json={"text": "What is a walkway?"}).json() == {"reply": "A plain answer."}
    assert json.loads(calls[0].data)["generationConfig"] == {"maxOutputTokens": 4096}


@pytest.mark.parametrize("lang,fragment", [("ko", "출력 한도"), ("en", "output limit")])
def test_truncated_json_never_applies_or_retries(client, monkeypatch, free, lang, fragment):
    before = client.get("/api/scene").json()
    # Even parseable JSON cannot authorize changes when the provider marks it incomplete.
    proposal = json.dumps({"ops": [{"op": "delete", "id": "table"}], "reply": "Removed"})
    calls = fake_transport(monkeypatch, raw=json.dumps({
        "candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": [{"text": proposal}]}}]
    }).encode())
    response = client.post(f"/api/command?lang={lang}", json={"text": "Delete table"})
    assert response.status_code == 502
    assert response.json()["code"] == "ai_output_truncated"
    assert fragment in response.json()["detail"]
    assert len(calls) == count(free) == 1
    assert client.get("/api/scene").json() == before


def test_empty_command_is_not_reported_as_success(client, monkeypatch, free):
    before = client.get("/api/scene").json()
    calls = fake_transport(monkeypatch, reply='{"ops":[],"reply":"The layout is already correct."}')
    response = client.post("/api/command?lang=en", json={"text": "소파를 삭제해 줘"})
    assert response.status_code == 502
    assert response.json()["code"] == "ai_no_action"
    assert "not changed" in response.json()["detail"]
    assert len(calls) == count(free) == 2
    assert client.get("/api/scene").json() == before


def test_empty_command_can_retry_to_exact_sofa_delete(client, monkeypatch, free):
    before = client.get("/api/scene").json()
    replies = iter([
        '{"ops":[],"reply":"The layout is already correct."}',
        '{"ops":[{"op":"delete","id":"sofa"}],"reply":"Deleted the sofa."}',
    ])
    calls = fake_transport(monkeypatch, reply=lambda: next(replies))
    response = client.post("/api/command?lang=en", json={"text": "소파를 삭제해 줘"})
    assert response.status_code == 200 and response.json()["applied"]
    assert response.json()["ops"] == [{"op": "delete", "id": "sofa"}]
    after = client.get("/api/scene").json()
    assert after["equipment"] == [item for item in before["equipment"] if item["id"] != "sofa"]
    assert after["structures"] == before["structures"] and after["rooms"] == before["rooms"]
    assert len(calls) == count(free) == 2
    assert "No operations proposed" in json.loads(calls[1].data)["contents"][0]["parts"][0]["text"]


@pytest.mark.parametrize("reply", [
    '```json\n{"ops":[{"op":"delete","id":"sofa"}],"reply":"Deleted"}\n```',
    '{"ops":[{"op":"delete","id":"sofa"}]}',
])
def test_schema_contract_violation_is_not_repaired_or_applied(client, monkeypatch, free, reply):
    before = client.get("/api/scene").json()
    calls = fake_transport(monkeypatch, reply=reply)
    response = client.post("/api/command", json={"text": "소파를 삭제해 줘"})
    assert response.status_code == 502 and response.json()["code"] == "ai_invalid_response"
    assert len(calls) == count(free) == 1
    assert client.get("/api/scene").json() == before


def test_legacy_fenced_json_compatibility(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("LLM_PROVIDER", "legacy")
    monkeypatch.setattr(llm, "llm_text", lambda *a, **kw: '```json\n{"ops":[],"reply":"Legacy"}\n```')
    assert llm._call_claude("test") == {"ops": [], "reply": "Legacy"}
