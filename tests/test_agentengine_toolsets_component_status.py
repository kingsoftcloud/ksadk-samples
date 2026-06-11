from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "02-use-cases/agentengine-toolsets/langgraph"


def _load_agent_module(monkeypatch, env: dict[str, str]):
    relevant_keys = {
        "KSADK_SKILL_RUNTIME_BACKEND",
        "KSADK_SKILL_RUNTIME_AGENT_PATH",
        "KSADK_SKILL_RUNTIME_TEMPLATE_ID",
        "KSADK_SANDBOX_BACKEND",
        "KSADK_SANDBOX_TEMPLATE_ID",
        "E2B_API_URL",
        "E2B_API_KEY",
        "E2B_TEMPLATE_ID",
        "KSADK_WORKSPACE_ROOT",
        "AGENTENGINE_WORKSPACE_ROOT",
        "WORKSPACE_ROOT",
    }
    for key in relevant_keys:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    module_name = "agentengine_toolsets_langgraph_agent_under_test"
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(SAMPLE))
    try:
        spec = importlib.util.spec_from_file_location(module_name, SAMPLE / "agent.py")
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        for value in (str(SAMPLE), str(ROOT)):
            try:
                sys.path.remove(value)
            except ValueError:
                pass
        sys.modules.pop(module_name, None)


def test_local_process_skill_runtime_does_not_require_template_or_e2b_key(monkeypatch):
    module = _load_agent_module(
        monkeypatch,
        {
            "KSADK_SKILL_RUNTIME_BACKEND": "local_process",
            "KSADK_SKILL_RUNTIME_AGENT_PATH": "/tmp/skill-runtime-agent.py",
        },
    )

    status = module._resolve_skill_runtime_status()

    assert status["configured"] is True
    assert status["effective_backend"] == "local_process"
    assert status["template_required"] is False
    assert status["template_configured"] is False
    assert status["e2b_api_key_required"] is False
    assert status["missing_config"] == []


def test_e2b_skill_runtime_requires_sandbox_template_and_e2b_key(monkeypatch):
    module = _load_agent_module(monkeypatch, {"KSADK_SKILL_RUNTIME_BACKEND": "e2b"})

    status = module._resolve_skill_runtime_status()

    assert status["configured"] is False
    assert status["effective_backend"] == "e2b"
    assert status["template_required"] is True
    assert status["template_configured"] is False
    assert status["missing_config"] == ["KSADK_SANDBOX_TEMPLATE_ID", "E2B_API_KEY"]


def test_sandbox_template_without_runtime_backend_infers_e2b(monkeypatch):
    module = _load_agent_module(
        monkeypatch,
        {
            "KSADK_SANDBOX_TEMPLATE_ID": "tmpl-public-demo",
            "E2B_API_KEY": "test-e2b-key",
        },
    )

    status = module._resolve_skill_runtime_status()

    assert status["configured"] is True
    assert status["backend"] == ""
    assert status["effective_backend"] == "e2b"
    assert status["template_source"] == "KSADK_SANDBOX_TEMPLATE_ID"
    assert status["missing_config"] == []


def test_e2b_template_id_is_reported_as_ignored_not_used(monkeypatch):
    module = _load_agent_module(
        monkeypatch,
        {
            "KSADK_SKILL_RUNTIME_BACKEND": "e2b",
            "E2B_TEMPLATE_ID": "ignored-template",
            "E2B_API_KEY": "test-e2b-key",
        },
    )

    runtime = module._resolve_skill_runtime_status()
    sandbox = module._resolve_sandbox_status()

    assert runtime["configured"] is False
    assert runtime["template_configured"] is False
    assert runtime["ignored_env"] == ["E2B_TEMPLATE_ID"]
    assert "KSADK_SANDBOX_TEMPLATE_ID" in runtime["missing_config"]
    assert sandbox["ignored_env"] == ["E2B_TEMPLATE_ID"]
