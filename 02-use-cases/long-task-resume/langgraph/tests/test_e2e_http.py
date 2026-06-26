from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def load_e2e(monkeypatch: Any, **env: str):
    sample_dir = Path(__file__).parents[1]
    module_name = "long_task_resume_e2e_http_under_test"
    sys.modules.pop(module_name, None)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    spec = importlib.util.spec_from_file_location(module_name, sample_dir / "e2e_http.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_skip_create_session_allows_runtime_owned_response_session(monkeypatch: Any):
    module = load_e2e(
        monkeypatch,
        LONG_TASK_E2E_SKIP_CREATE_SESSION="1",
        LONG_TASK_E2E_AGENT_ID="ar-runtime-id",
    )
    calls: list[tuple[str, dict[str, Any]]] = []
    checkpoint_call_count = 0

    def fake_post(path: str, payload: dict[str, Any], *, timeout: int = 30):
        nonlocal checkpoint_call_count
        del timeout
        calls.append((path, payload))
        if path == "/agentengine/api/v1/ListSessionEvents":
            return {
                "Data": {
                    "Events": [
                        {
                            "EventType": "run_status",
                            "InvocationId": "longtask_run_123456789abc",
                            "Content": {"status": "cancelled"},
                        },
                        {
                            "Metadata": {"run_id": "run_123456789abc"},
                            "Content": {},
                        },
                    ]
                }
            }
        if path == "/agentengine/api/v1/ListSessionCheckpoints":
            checkpoint_call_count += 1
            checkpoints = [
                {"CheckpointId": "ckpt-1", "Stage": "规划研究问题", "Status": "completed"},
                {"CheckpointId": "ckpt-2", "Stage": "检索公开网页", "Status": "completed"},
            ]
            if checkpoint_call_count >= 3:
                checkpoints.append(
                    {"CheckpointId": "ckpt-3", "Stage": "生成研究报告", "Status": "completed"}
                )
            return {
                "Data": {
                    "Checkpoints": checkpoints
                }
            }
        if path == "/agentengine/api/v1/CancelRun":
            return {"Data": {"Cancelled": True}}
        if path == "/agentengine/api/v1/GetCheckpointResumePreview":
            return {
                "Data": {
                    "Preview": {
                        "Summary": {"RunId": "run_123456789abc"},
                        "ToolReceipts": [],
                    }
                }
            }
        raise AssertionError(f"unexpected POST {path}")

    def fake_sse_post(path: str, payload: dict[str, Any], *, timeout: int = 240):
        del payload, timeout
        calls.append((path, {}))
        if path == "/v1/responses":
            launch_text = "我开始做一份 Deep Research。\n\n研究主题：`测试问题`"
            return [{"text": launch_text}], launch_text
        if path == "/agentengine/api/v1/ResumeRun":
            return [{"text": "已完成阶段直接跳过 deepresearch-report.md"}], "已完成阶段直接跳过 deepresearch-report.md"
        raise AssertionError(f"unexpected SSE {path}")

    monkeypatch.setattr(module, "_post", fake_post)
    monkeypatch.setattr(module, "_sse_post", fake_sse_post)
    module.main()

    assert not any(path == "/agentengine/api/v1/CreateSession" for path, _ in calls)
    action_payloads = [
        payload
        for path, payload in calls
        if path
        in {
            "/agentengine/api/v1/ListSessionCheckpoints",
            "/agentengine/api/v1/CancelRun",
            "/agentengine/api/v1/GetCheckpointResumePreview",
        }
    ]
    assert action_payloads
    assert all(payload["AgentId"] == "ar-runtime-id" for payload in action_payloads)
