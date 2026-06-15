from __future__ import annotations

import json
import os
import time
import urllib.request
from datetime import datetime
from typing import Any


BASE_URL = os.environ.get("LONG_TASK_E2E_BASE_URL", "http://localhost:9876").rstrip("/")
AGENT_ID = os.environ.get("LONG_TASK_E2E_AGENT_ID", "long-task-resume")
MODEL = os.environ.get("OPENAI_MODEL_NAME", "glm-5.1")
SKIP_CREATE_SESSION = os.environ.get("LONG_TASK_E2E_SKIP_CREATE_SESSION", "").lower() in {"1", "true", "yes"}
SESSION_ID = os.environ.get(
    "LONG_TASK_E2E_SESSION_ID",
    "long-task-e2e-" + datetime.now().strftime("%Y%m%d%H%M%S"),
)
QUESTION = os.environ.get(
    "LONG_TASK_E2E_QUESTION",
    "调研 GLP-1 受体激动剂在肥胖和 2 型糖尿病治疗中的临床证据、药物经济学、支付准入和真实世界安全性。",
)


def _post(path: str, payload: dict[str, Any], *, timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _sse_post(path: str, payload: dict[str, Any], *, timeout: int = 240) -> tuple[list[dict[str, Any]], str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    events: list[dict[str, Any]] = []
    raw_events: list[str] = []
    with urllib.request.urlopen(request, timeout=timeout) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            body = line[5:].strip()
            if body == "[DONE]":
                break
            raw_events.append(body)
            try:
                events.append(json.loads(body))
            except json.JSONDecodeError:
                events.append({"raw": body})
    return events, "\n".join(raw_events)


def _contains_text(events: list[dict[str, Any]], raw_text: str, needle: str) -> bool:
    structured_text = json.dumps(events, ensure_ascii=False)
    if needle in structured_text or needle in raw_text:
        return True
    try:
        return needle in raw_text.encode("utf-8").decode("unicode_escape")
    except UnicodeDecodeError:
        return False


def _debug_excerpt(events: list[dict[str, Any]], raw_text: str, *, limit: int = 1200) -> str:
    compact = raw_text or json.dumps(events[:5], ensure_ascii=False)
    compact = compact.replace("\n", "\\n")
    if len(compact) > limit:
        return compact[:limit] + "..."
    return compact


def _session_events() -> list[dict[str, Any]]:
    return _post("/agentengine/api/v1/ListSessionEvents", {"SessionId": SESSION_ID})["Data"]["Events"]


def _session_checkpoints(run_id: str) -> list[dict[str, Any]]:
    return _post(
        "/agentengine/api/v1/ListSessionCheckpoints",
        {"AgentId": AGENT_ID, "SessionId": SESSION_ID, "RunId": run_id},
    )["Data"]["Checkpoints"]


def _find_run_id() -> str:
    for event in _session_events():
        metadata = event.get("Metadata") if isinstance(event.get("Metadata"), dict) else {}
        run_id = metadata.get("run_id")
        if isinstance(run_id, str) and run_id.startswith("run_"):
            return run_id
        content = event.get("Content") if isinstance(event.get("Content"), dict) else {}
        detail = str(content.get("detail") or "")
        if "background_long_task_started:run_" in detail:
            return detail.rsplit(":", 1)[-1]
    return ""


def _wait_for_checkpoints(run_id: str, minimum: int, *, timeout_seconds: int = 60) -> list[dict[str, Any]]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        checkpoints = _session_checkpoints(run_id)
        if len(checkpoints) >= minimum:
            return checkpoints
        time.sleep(1)
    return _session_checkpoints(run_id)


def _wait_for_terminal_status(invocation_id: str, *, timeout_seconds: int = 30) -> str:
    deadline = time.monotonic() + timeout_seconds
    terminal = {"failed", "cancelled", "completed"}
    latest = ""
    while time.monotonic() < deadline:
        statuses = [
            event
            for event in _session_events()
            if event.get("EventType") == "run_status" and event.get("InvocationId") == invocation_id
        ]
        if statuses:
            latest = str((statuses[-1].get("Content") or {}).get("status") or "")
            if latest in terminal:
                return latest
        time.sleep(1)
    return latest


def main() -> None:
    if not SKIP_CREATE_SESSION:
        _post(
            "/agentengine/api/v1/CreateSession",
            {"AgentId": AGENT_ID, "UserId": "user", "SessionId": SESSION_ID},
        )
    launch_events, launch_raw_text = _sse_post(
        "/v1/responses",
        {"model": MODEL, "conversation": SESSION_ID, "input": QUESTION, "stream": True},
        timeout=90,
    )
    if not _contains_text(launch_events, launch_raw_text, "Deep Research") or not _contains_text(
        launch_events,
        launch_raw_text,
        "研究主题",
    ):
        raise AssertionError(
            "launch response did not describe the DeepResearch background run: "
            + _debug_excerpt(launch_events, launch_raw_text)
        )

    run_id = ""
    for _ in range(30):
        run_id = _find_run_id()
        if run_id:
            break
        time.sleep(1)
    if not run_id:
        raise AssertionError("background run_id was not recorded in session events")

    initial_checkpoints = _wait_for_checkpoints(run_id, 2)
    if len(initial_checkpoints) < 2:
        raise AssertionError("background run did not produce at least two LangGraph checkpoints")

    invocation_id = f"longtask_{run_id}"
    cancel_result = _post(
        "/agentengine/api/v1/CancelRun",
        {"AgentId": AGENT_ID, "InvocationId": invocation_id},
    )["Data"]
    if not cancel_result.get("Cancelled"):
        raise AssertionError(f"CancelRun was not accepted: {cancel_result}")
    cancel_status = _wait_for_terminal_status(invocation_id)
    if cancel_status != "cancelled":
        raise AssertionError(f"background run did not stop as cancelled, latest={cancel_status}")

    selected = _session_checkpoints(run_id)[-1]
    preview = _post(
        "/agentengine/api/v1/PreviewCheckpointResume",
        {
            "AgentId": AGENT_ID,
            "SessionId": SESSION_ID,
            "RunId": run_id,
            "CheckpointId": selected["CheckpointId"],
        },
    )["Data"]["Preview"]
    if preview["Summary"]["RunId"] != run_id:
        raise AssertionError("PreviewCheckpointResume returned a different run_id")

    resume_events, resume_raw_text = _sse_post(
        "/agentengine/api/v1/ResumeRun",
        {
            "AgentId": AGENT_ID,
            "SessionId": SESSION_ID,
            "RunId": run_id,
            "CheckpointId": selected["CheckpointId"],
            "ResumeAttemptId": "resume-http-e2e",
            "InvocationId": "resume-http-e2e",
            "Stream": True,
            "Model": MODEL,
        },
        timeout=240,
    )
    if not _contains_text(
        resume_events,
        resume_raw_text,
        "已完成阶段直接跳过",
    ) or not _contains_text(resume_events, resume_raw_text, "deepresearch-report.md"):
        raise AssertionError("ResumeRun output did not show skipped stages and final report")

    final_checkpoints = _session_checkpoints(run_id)
    empty_checkpoints = [
        checkpoint
        for checkpoint in final_checkpoints
        if not checkpoint.get("Stage") or not checkpoint.get("Status")
    ]
    if empty_checkpoints:
        raise AssertionError(f"checkpoint list contains empty display rows: {empty_checkpoints}")
    if len(final_checkpoints) < len(initial_checkpoints) + 1:
        raise AssertionError("ResumeRun did not append any later checkpoints")

    print(
        json.dumps(
            {
                "ok": True,
                "base_url": BASE_URL,
                "agent_id": AGENT_ID,
                "skip_create_session": SKIP_CREATE_SESSION,
                "session_id": SESSION_ID,
                "run_id": run_id,
                "initial_checkpoint_count": len(initial_checkpoints),
                "preview_receipt_count": len(preview.get("ToolReceipts") or []),
                "resume_event_count": len(resume_events),
                "final_checkpoint_count": len(final_checkpoints),
                "final_stages": [checkpoint.get("Stage") for checkpoint in final_checkpoints],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
