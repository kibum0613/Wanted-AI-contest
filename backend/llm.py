"""LLM explanation layer (Explain + Learn).

Role separation: every number and every fix candidate comes from the
deterministic engines (detector/resolver). The LLM only turns those verified
facts into an engineer-friendly explanation and cites similar past cases.

Public backend: explicitly selected, quota-guarded free Gemini with no fallback.
Local legacy mode retains API-key priority, Claude CLI, and template fallback.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import socket
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from backend.i18n import LANGUAGE, language_instruction
from backend.deployment import (
    AIError, CALL_SLOT, MAX_OUTPUT_CHARS, MAX_PROMPT_CHARS, MAX_RESPONSE_BYTES,
    config_error, free_mode, invalid_response, public_mode, quota_state, validate_config,
)

KNOWLEDGE_FILE = Path(__file__).resolve().parent / "data" / "knowledge.json"
CLAUDE_TIMEOUT_S = 90
HTTP_TIMEOUT_S = 60
EXPLANATION_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "why": {"type": "STRING"},
        "impact": {"type": "ARRAY", "items": {"type": "STRING"}, "minItems": 1, "maxItems": 3},
        "recommendation": {"type": "STRING"},
        "past_case": {"type": "STRING"},
    },
    "required": ["why", "impact", "recommendation", "past_case"],
}
COMMAND_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "ops": {
            "type": "ARRAY", "maxItems": 20,
            "items": {
                "type": "OBJECT",
                "description": "Include only the fields needed by the chosen operation; omit unused optional fields.",
                "properties": {
                    "op": {"type": "STRING", "enum": ["place", "move", "rotate", "delete", "add_equipment"]},
                    "id": {"type": "STRING"},
                    "type": {"type": "STRING", "enum": [
                        "bed", "wardrobe", "desk", "sofa", "fridge", "bookshelf",
                        "tv_stand", "washing_machine", "table",
                    ]},
                    "room": {"type": "STRING"},
                    "near": {"type": "STRING"},
                    "delta": {"type": "ARRAY", "items": {"type": "NUMBER"}, "minItems": 3, "maxItems": 3},
                    "center": {"type": "ARRAY", "items": {"type": "NUMBER"}, "minItems": 2, "maxItems": 2},
                },
                "required": ["op"],
            },
        },
        "reply": {
            "type": "STRING",
            "description": "Describe the requested operations. If no operation is possible, explain why; do not claim completion.",
        },
    },
    "required": ["ops", "reply"],
}


def _load_env() -> None:
    """Load KEY=VALUE pairs from repo-root .env (gitignored) into os.environ."""
    if public_mode() or free_mode():
        return
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


_load_env()


def _load_knowledge() -> dict:
    return json.loads(KNOWLEDGE_FILE.read_text(encoding="utf-8"))


def retrieve_knowledge(violation: dict) -> dict:
    """RAG-lite: select rules/cases whose tags match the violation."""
    kb = _load_knowledge()
    specific = {violation["a"].get("type", ""), violation["a"]["id"]}
    if violation["code"] == "ZONE_INTRUSION":
        specific.update(violation["b"]["id"].split("_"))
    relevant = [r for r in kb["rules"] if violation["code"] in r["tags"]]
    exact = [r for r in relevant if specific.intersection(r["tags"])]
    cases = [c for c in kb["cases"] if violation["code"] in c["tags"]]
    cases.sort(key=lambda c: not bool(specific.intersection(c["tags"])))
    return {
        "rules": (exact or relevant)[:2],
        "cases": cases[:2],
    }


def _build_prompt(violation: dict, candidates: list[dict], knowledge: dict) -> str:
    facts = {
        "violation": violation,
        "verified_fix_candidates": [
            {k: c[k] for k in ("option", "description", "impact",
                               "displacement_mm", "violations_after", "recommended")}
            for c in candidates
        ],
        "design_rules": knowledge["rules"],
        "past_cases": knowledge["cases"],
    }
    return f"""당신은 1인 주택 인테리어 배치 검토 전문가입니다. 아래 JSON은 결정론적 기하 검증 엔진이 검출한 배치 문제와, 시뮬레이션으로 이미 검증된 해결안 후보입니다.

{json.dumps(facts, ensure_ascii=False, indent=1)}

위 데이터만 근거로 거주자에게 보고서를 작성하세요. 반드시 아래 JSON 형식으로만 답하세요(마크다운 코드블록 없이 순수 JSON만):
{{
 "why": "이 문제가 왜 불편/위험한지 2-3문장 (관련 규칙 근거 인용, 생활 시나리오로 설명)",
 "impact": ["예상되는 실생활 영향 3개 (편의/안전/위생 관점)"],
 "recommendation": "추천안과 그 이유 2-3문장 (다른 안과의 비교 포함)",
 "past_case": "가장 유사한 과거 배치 사례 요약과 당시 해결 방법 1-2문장"
}}

규칙: 제공된 수치를 절대 바꾸거나 새로 만들지 마세요. 제공된 데이터에 없는 사실을 지어내지 마세요.""" + language_instruction()


def _claude_text(prompt: str) -> str | None:
    """Run claude CLI headless and return the raw text reply."""
    exe = shutil.which("claude")
    if exe is None:
        return None
    try:
        proc = subprocess.run(
            [exe, "-p", prompt, "--output-format", "json",
             "--model", "haiku",
             "--disallowed-tools", "*"],
            capture_output=True, text=True, encoding="utf-8",
            timeout=CLAUDE_TIMEOUT_S,
        )
        if proc.returncode != 0:
            return None
        envelope = json.loads(proc.stdout)
        return (envelope.get("result") or "").strip() or None
    except Exception:
        return None


def _post_json(url: str, payload: dict, headers: dict) -> dict | None:
    try:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", **headers})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as resp:
            return json.load(resp)
    except Exception:
        return None


def _gemini_text(prompt: str) -> str | None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    out = _post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"contents": [{"parts": [{"text": prompt}]}],
         # this workload needs no deliberation; thinking multiplies latency
         "generationConfig": {"thinkingConfig": {"thinkingLevel": "minimal"}}},
        {"x-goog-api-key": key})
    try:
        parts = out["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        return text.strip() or None
    except Exception:
        return None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _free_gemini_text(prompt: str, *, response_schema: dict | None = None) -> str:
    path = validate_config()
    if not isinstance(prompt, str) or len(prompt) > MAX_PROMPT_CHARS or len(prompt.encode("utf-8")) > 64000:
        raise AIError("ai_prompt_limit", 413, "AI 요청이 너무 큽니다. 배치나 대화를 줄여주세요.",
                      "The AI request is too large. Reduce the scene or conversation.")
    if not CALL_SLOT.acquire(blocking=False):
        raise AIError("ai_busy", 429, "다른 방문자의 AI 요청을 처리 중입니다. 잠시 후 다시 시도하세요.",
                      "Another visitor's AI request is in progress. Please try shortly.", 5)
    try:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 4096},
        }
        if response_schema is not None:
            payload["generationConfig"].update({
                "responseMimeType": "application/json",
                "responseSchema": response_schema,
            })
        request = urllib.request.Request(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
        opener = urllib.request.build_opener(_NoRedirect)
        quota_state(path, reserve=True)
        try:
            with opener.open(request, timeout=HTTP_TIMEOUT_S) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise invalid_response()
            out = json.loads(raw)
            candidate = out["candidates"][0]
            if candidate.get("finishReason") == "MAX_TOKENS":
                raise AIError("ai_output_truncated", 502,
                              "AI 응답이 출력 한도에서 중단되어 적용하지 않았습니다. 더 짧고 간단한 요청으로 다시 시도하세요.",
                              "The AI response reached its output limit and was not applied. Try a shorter, simpler request.")
            if candidate.get("finishReason") != "STOP":
                raise invalid_response()
            parts = candidate["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
            if not text or len(text) > MAX_OUTPUT_CHARS:
                raise invalid_response()
            return text
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise config_error() from exc
            if exc.code == 429:
                raise AIError("ai_provider_quota", 429, "무료 Gemini 한도에 도달했습니다. 나중에 다시 시도하세요.",
                              "The free Gemini provider quota is exhausted. Try later.", 60) from exc
            raise AIError("ai_provider_error", 502, "Gemini 제공자 요청에 실패했습니다. 다른 제공자로 전환하지 않습니다.",
                          "The Gemini provider request failed. No other provider will be used.") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise AIError("ai_timeout", 504, "Gemini 응답 시간이 초과되었습니다.",
                          "The Gemini request timed out.") from exc
        except (urllib.error.URLError, OSError) as exc:
            raise AIError("ai_unavailable", 503, "Gemini에 연결할 수 없습니다. 나중에 다시 시도하세요.",
                          "Gemini is unavailable. Please try later.") from exc
        except (ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
            raise invalid_response() from exc
    finally:
        CALL_SLOT.release()


def _openai_compat_text(prompt: str, url: str, key: str, model: str) -> str | None:
    out = _post_json(url, {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }, {"Authorization": f"Bearer {key}"})
    try:
        return out["choices"][0]["message"]["content"].strip() or None
    except Exception:
        return None


def llm_text(prompt: str, *, response_schema: dict | None = None) -> str | None:
    """Fast-provider dispatch: Gemini/Groq/OpenAI via direct HTTP if an API key
    is configured (1-3s), otherwise fall back to the Claude Code CLI (slower
    because every call cold-starts a full CLI session)."""
    validate_config()
    if free_mode():
        return _free_gemini_text(prompt, response_schema=response_schema)
    if os.environ.get("GEMINI_API_KEY"):
        r = _gemini_text(prompt)
        if r:
            return r
    if os.environ.get("GROQ_API_KEY"):
        r = _openai_compat_text(
            prompt, "https://api.groq.com/openai/v1/chat/completions",
            os.environ["GROQ_API_KEY"],
            os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"))
        if r:
            return r
    if os.environ.get("OPENAI_API_KEY"):
        r = _openai_compat_text(
            prompt, "https://api.openai.com/v1/chat/completions",
            os.environ["OPENAI_API_KEY"],
            os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
        if r:
            return r
    return _claude_text(prompt)


def _call_claude(prompt: str, *, response_schema: dict | None = None) -> dict | None:
    """Run the configured LLM and parse its reply as JSON."""
    text = llm_text(prompt, response_schema=response_schema)
    if text is None:
        return None
    try:
        # Legacy providers may wrap JSON; schema-constrained public responses must be JSON.
        if not free_mode() and text.startswith("```"):
            text = text.strip("`")
            text = text[text.find("{"):text.rfind("}") + 1]
        result = json.loads(text)
        if free_mode() and not isinstance(result, dict):
            raise invalid_response()
        return result
    except AIError:
        raise
    except Exception:
        if free_mode():
            raise invalid_response()
        return None


def _fallback(violation: dict, candidates: list[dict], knowledge: dict) -> dict:
    rule = knowledge["rules"][0] if knowledge["rules"] else None
    case = knowledge["cases"][0] if knowledge["cases"] else None
    rec = next((c for c in candidates if c.get("recommended")), None)
    if LANGUAGE.get() == "en":
        return {
            "why": violation["detail"],
            "impact": ["Access may be obstructed", "Furniture may be difficult to use"],
            "recommendation": (
                f"Option {rec['option']}: {rec['description']}. Impact: {rec['impact']}."
                if rec else "No automatic fix is available; manual review is needed."),
            "past_case": (f"Related knowledge-base case: {case['id']}."
                          if case else "No related case is registered."),
            "llm": False,
        }
    return {
        "why": (f"{violation['detail']} — " + (rule["content"] if rule else "배치 기준 위반입니다.")),
        "impact": ["일상 생활 동선 불편", "야간·비상시 안전사고 위험", "가구 사용성 저하 (개폐/접근 불편)"],
        "recommendation": (f"{rec['option']}안({rec['description']})을 권장합니다. 영향: {rec['impact']}."
                           if rec else "자동 해결안이 없어 수동 검토가 필요합니다."),
        "past_case": (f"[{case['project']}] {case['problem']} → {case['resolution']}. {case['lesson']}"
                      if case else "유사 사례가 등록되어 있지 않습니다."),
        "llm": False,
    }


def explain_violation(violation: dict, candidates: list[dict]) -> dict[str, Any]:
    validate_config()
    key = json.dumps([os.environ.get("LLM_PROVIDER", "legacy"), LANGUAGE.get(), violation, candidates],
                     sort_keys=True, ensure_ascii=False)
    if key in _CACHE:
        return _CACHE[key]
    knowledge = retrieve_knowledge(violation)
    prompt = _build_prompt(violation, candidates, knowledge)
    result = (_call_claude(prompt, response_schema=EXPLANATION_RESPONSE_SCHEMA)
              if free_mode() else _call_claude(prompt))
    if free_mode() and (not isinstance(result, dict)
                       or not all(isinstance(result.get(k), str) for k in ("why", "recommendation", "past_case"))
                       or not isinstance(result.get("impact"), list)
                       or not all(isinstance(v, str) for v in result["impact"])):
        raise invalid_response()
    if result is None:
        result = _fallback(violation, candidates, knowledge)
    else:
        result["llm"] = True
    result["knowledge_used"] = {
        "rules": [r["id"] for r in knowledge["rules"]],
        "cases": [c["id"] for c in knowledge["cases"]],
    }
    if len(_CACHE) >= 128:
        _CACHE.pop(next(iter(_CACHE)))
    _CACHE[key] = result
    return result


_CACHE: dict[str, dict] = {}
