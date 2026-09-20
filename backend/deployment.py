"""Fail-closed public-demo configuration and durable, conservative AI budgets."""
from __future__ import annotations

from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import threading
import time
from uuid import uuid4

from backend.i18n import tr

MAX_PROMPT_CHARS = 24000
MAX_OUTPUT_CHARS = 12000
MAX_RESPONSE_BYTES = 65536
MAX_BODY_BYTES = 131072
CALL_SLOT = threading.BoundedSemaphore(1)
QUOTA_LOCK = threading.Lock()


class AIError(Exception):
    def __init__(self, code: str, status: int, ko: str, en: str, retry_after: int | None = None):
        self.code, self.status = code, status
        self.ko, self.en, self.retry_after = ko, en, retry_after
        super().__init__(code)

    @property
    def message(self):
        return tr(self.ko, self.en)


def config_error():
    return AIError("ai_configuration", 503, "무료 AI 설정 오류입니다. 운영자에게 문의하세요.",
                   "Free AI configuration is invalid. Contact the operator.")


def invalid_response():
    return AIError("ai_invalid_response", 502, "AI 응답 형식이 잘못되었습니다. 다시 시도하세요.",
                   "The AI returned an invalid response. Please try again.")


def public_mode() -> bool:
    return os.environ.get("APP_ENV", "local") == "production"


def free_mode() -> bool:
    return os.environ.get("LLM_PROVIDER", "legacy") == "gemini-free"


def validate_config() -> Path | None:
    if os.environ.get("APP_ENV", "local") not in {"local", "production"}:
        raise config_error()
    provider = os.environ.get("LLM_PROVIDER", "legacy")
    if provider not in {"legacy", "gemini-free"} or (public_mode() and provider != "gemini-free"):
        raise config_error()
    if not free_mode():
        return None
    if (os.environ.get("GEMINI_MODEL") != "gemini-3.5-flash-lite"
            or not os.environ.get("GEMINI_API_KEY", "").strip()
            or os.environ.get("GEMINI_FREE_TIER_ONLY") != "true"):
        raise config_error()
    quota = Path(os.environ.get("AI_QUOTA_FILE", ""))
    saved = Path(os.environ.get("SAVED_LAYOUT_PATH", ""))
    if not quota.is_absolute() or (public_mode() and not saved.is_absolute()):
        raise config_error()
    if public_mode() and (quota == saved or quota.parent == Path(__file__).resolve().parent / "data"
                          or Path(__file__).resolve().parent in saved.parents):
        raise config_error()
    return quota


def storage_error():
    return AIError("ai_quota_storage", 503, "AI 사용량 저장소를 사용할 수 없어 요청을 중단했습니다.",
                   "AI requests are disabled because quota storage is unavailable.")


def atomic_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name("." + path.name + "." + uuid4().hex + ".staging")
    try:
        with staging.open("x", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        staging.replace(path)
        if os.name != "nt":
            fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    finally:
        staging.unlink(missing_ok=True)


@contextmanager
def _file_lock(path: Path):
    # The inode is never replaced; data is replaced separately under this lock.
    path.parent.mkdir(parents=True, exist_ok=True)
    with QUOTA_LOCK, path.with_suffix(path.suffix + ".lock").open("a+b") as handle:
        if os.name == "nt":
            import msvcrt
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def quota_state(path: Path, *, reserve: bool = False, now: float | None = None) -> dict:
    """Reserve before HTTP, including failed calls/retries; never refund on uncertainty.

    Rolling 24-hour and 60-second windows are at least as strict as calendar-day
    quotas. A backward clock jump fails closed rather than discarding history.
    """
    now = time.time() if now is None else now
    try:
        with _file_lock(path):
            if path.exists():
                state = json.loads(path.read_text(encoding="utf-8"))
                if (not isinstance(state, dict) or state.get("version") != 1
                        or not isinstance(state.get("calls"), list)
                        or len(state["calls"]) > 400):
                    raise ValueError("invalid quota")
                calls = state["calls"]
                if any(type(t) not in (int, float) or not math.isfinite(t) or t < 0 or t > now
                       for t in calls):
                    raise ValueError("invalid timestamps or clock rollback")
            else:
                calls = []
            calls = sorted(t for t in calls if t > now - 86400)
            minute = [t for t in calls if t > now - 60]
            if reserve:
                if len(calls) >= 400:
                    raise AIError("ai_daily_quota", 429, "공용 AI 일일 한도(400회)에 도달했습니다. 나중에 다시 시도하세요.",
                                  "The shared AI daily quota (400 calls) is exhausted. Try later.",
                                  max(1, math.ceil(calls[0] + 86400 - now)))
                if len(minute) >= 10:
                    raise AIError("ai_minute_quota", 429, "공용 AI 분당 한도(10회)에 도달했습니다. 잠시 후 다시 시도하세요.",
                                  "The shared AI quota (10 calls/minute) is exhausted. Try shortly.",
                                  max(1, math.ceil(minute[0] + 60 - now)))
                calls.append(now)
            atomic_json(path, {"version": 1, "calls": calls})
            return {"minute_limit": 10, "day_limit": 400, "window": "rolling_24_hours"}
    except AIError:
        raise
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        raise storage_error() from exc


def validate_public_scene(scene) -> None:
    if not public_mode():
        return
    objects = scene.furniture + scene.structures + scene.rooms + scene.walkways
    valid = len(objects) <= 100 and len(scene.meta.name) <= 120
    boxes = [scene.meta.room] + [o.box for o in objects if hasattr(o, "box")]
    valid &= all(abs(v) <= 30 for box in boxes for v in box.min + box.max)
    valid &= all(len(o.id) <= 80 and len(o.name) <= 120 for o in objects)
    valid &= all(math.isfinite(v) and 0 <= v <= 10000 for v in scene.rules.model_dump().values())
    valid &= all(o.maintenance_clearance_mm is None or o.maintenance_clearance_mm <= 10000
                 for o in scene.furniture)
    for walkway in scene.walkways:
        valid &= (2 <= len(walkway.path) <= 100 and math.isfinite(walkway.diameter_mm)
                  and 0 < walkway.diameter_mm <= 10000)
        valid &= all(len(p) == 3 and all(math.isfinite(v) and abs(v) <= 30 for v in p)
                     for p in walkway.path)
    if not valid:
        raise AIError("scene_bounds", 422, "공용 데모 배치 크기 제한을 초과했습니다.",
                      "The scene exceeds the public demo size limits.")
