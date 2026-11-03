"""Small demo event log, intentionally omitting tool arguments and payloads."""

import contextvars
import functools
import json
import os
from pathlib import Path
import threading
import time
import uuid

TRACE = contextvars.ContextVar("demo_trace", default=None)
LOCK = threading.Lock()


def emit(event, **fields):
    state = Path(
        os.environ.get(
            "TRAILSHOP_DEMO_STATE", Path.home() / ".local/state/trailshop-codex"
        )
    )
    state.mkdir(parents=True, exist_ok=True)
    row = {
        "time": time.strftime("%H:%M:%S"),
        "trace": TRACE.get(),
        "event": event,
        **fields,
    }
    with LOCK, (state / "events.jsonl").open("a") as f:
        f.write(json.dumps(row) + "\n")


def traced(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        token = TRACE.set(uuid.uuid4().hex[:8])
        started = time.perf_counter()
        emit("tool.started", tool=fn.__name__)
        try:
            result = fn(*args, **kwargs)
            emit(
                "tool.succeeded",
                tool=fn.__name__,
                duration_ms=round((time.perf_counter() - started) * 1000),
                outcome=result.get("status", "ok")
                if isinstance(result, dict)
                else "ok",
            )
            return result
        except Exception as exc:
            emit(
                "tool.failed",
                tool=fn.__name__,
                duration_ms=round((time.perf_counter() - started) * 1000),
                error_type=type(exc).__name__,
            )
            raise
        finally:
            TRACE.reset(token)

    return wrapped
