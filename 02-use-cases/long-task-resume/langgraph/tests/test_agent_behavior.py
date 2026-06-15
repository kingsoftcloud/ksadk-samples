from __future__ import annotations

import asyncio
import importlib
import importlib.util
import sys
from types import SimpleNamespace
from pathlib import Path
from typing import Any


def load_agent(monkeypatch: Any, tmp_path: Path):
    monkeypatch.setenv("LONG_TASK_RESUME_DEMO_MODE", "fixture")
    monkeypatch.setenv("LONG_TASK_STAGE_DELAY_SECONDS", "0")
    monkeypatch.setenv("LONG_TASK_RESUME_WORKSPACE_DIR", str(tmp_path / "workspace"))
    monkeypatch.setenv("AGENTENGINE_UI_DIR", str(tmp_path / "ui"))
    monkeypatch.setenv("KSADK_STM_PATH", str(tmp_path / "ui" / "sessions.sqlite"))
    sample_dir = Path(__file__).parents[1]
    module_name = "long_task_resume_langgraph_agent_under_test"
    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(sample_dir))
    try:
        spec = importlib.util.spec_from_file_location(module_name, sample_dir / "agent.py")
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        try:
            sys.path.remove(str(sample_dir))
        except ValueError:
            pass


def collect_stream(runner: Any, payload: dict[str, Any]) -> list[dict[str, Any]]:
    async def _run() -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        async for event in runner.stream(payload):
            events.append(event)
        return events

    return asyncio.run(_run())


def make_runner(agent_module: Any):
    class Detection:
        name = "long-task-pg-e2e"

    return agent_module.LongTaskE2ERunner(Detection(), str(Path(__file__).parents[1]))


def make_langgraph_checkpoint(agent_module: Any, runner: Any, session_id: str, run_id: str, stage_count: int):
    async def _run() -> tuple[str, dict[str, Any]]:
        graph = runner._get_fixture_graph()
        config = runner._get_config(f"{session_id}:{run_id}")
        graph_input = agent_module._initial_state({"input": "调研 GLP-1 受体激动剂在肥胖和 2 型糖尿病治疗中的临床证据、药物经济学、支付准入和真实世界安全性"})
        checkpoint_id = ""
        framework_ref: dict[str, Any] = {}
        for stage in agent_module.REPORT_STAGES[:stage_count]:
            _values, framework_ref, checkpoint_id, config = await runner._invoke_graph_step(
                graph,
                graph_input=graph_input,
                config=config,
                stage=stage,
                payload={},
            )
            graph_input = None
        return checkpoint_id, framework_ref

    return asyncio.run(_run())


def test_normal_chat_does_not_emit_checkpoints(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL_NAME", raising=False)

    events = collect_stream(
        make_runner(agent_module),
        {"session_id": "sess-chat", "invocation_id": "chat-1", "input": "你好"},
    )

    assert [event["type"] for event in events] == ["text", "final"]
    assert "模型未配置" in events[-1]["output"]
    assert not any(event["type"] == "checkpoint" for event in events)


def test_checkpoint_explanation_is_normal_chat_not_background_job(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL_NAME", raising=False)

    events = collect_stream(
        make_runner(agent_module),
        {"session_id": "sess-chat", "invocation_id": "chat-2", "input": "checkpoint 和 resume 是什么意思？"},
    )

    assert [event["type"] for event in events] == ["text", "final"]
    assert "后台做一份通用 DeepResearch" not in events[-1]["output"]
    assert "模型未配置" in events[-1]["output"]


def test_research_question_emits_only_launch_message(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)

    events = collect_stream(
        make_runner(agent_module),
        {
            "session_id": "sess-long",
            "invocation_id": "launch-1",
            "input": "调研 GLP-1 受体激动剂在肥胖和 2 型糖尿病治疗中的临床证据、药物经济学、支付准入和真实世界安全性",
        },
    )

    assert [event["type"] for event in events] == ["text", "final"]
    assert "Deep Research" in events[-1]["output"]
    assert "研究主题" in events[-1]["output"]
    assert "成熟深度研究 Agent" in events[-1]["output"]
    assert "公开资料" in events[-1]["output"]
    assert "web_search 子图" not in events[-1]["output"]
    assert "run_id" not in events[-1]["output"]
    assert "invocation_id" not in events[-1]["output"]
    assert "checkpoint" not in events[-1]["output"]
    assert "LangGraph" not in events[-1]["output"]
    assert "模拟一次外部工具失败" not in events[-1]["output"]
    assert not any(event["type"] == "checkpoint" for event in events)


def test_non_streaming_research_question_starts_research_without_internal_report(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    runner = make_runner(agent_module)

    result = asyncio.run(
        runner.invoke(
            {
                "session_id": "sess-nonstream",
                "invocation_id": "invoke-1",
                "input": "帮我研究一下 LLM 领域最新进展",
            }
        )
    )

    output = result["output"]
    assert "Deep Research" in output
    assert "研究主题" in output
    assert "ResumeRun 结果" not in output
    assert "tool receipt" not in output
    assert "checkpoint" not in output
    assert "LangGraph" not in output


def test_status_answer_reads_like_progress_not_internal_state(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    runner = make_runner(agent_module)
    runner._background_runs_by_session["sess-progress"] = "run-progress"

    class FakeService:
        async def get_events(self, session_id: str):
            del session_id
            return [
                SimpleNamespace(
                    event_type="run_checkpoint",
                    metadata={
                        "run_id": "run-progress",
                        "stage": "筛选证据并去重",
                        "summary": "可引用证据清单已经确定，恢复后直接进入交叉分析。",
                        "next_action": "继续交叉分析发现",
                    },
                )
            ]

    monkeypatch.setattr(agent_module, "resolve_session_service", lambda: FakeService())

    output = asyncio.run(runner._render_status_answer("sess-progress"))

    assert "当前进度" in output
    assert "筛选证据并去重" in output
    assert "交叉分析" in output
    assert "run-progress" not in output
    assert "LangGraph" not in output
    assert "checkpoint" not in output


def test_builtin_search_parser_extracts_real_result_shape(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    html = """
    <html><body>
      <li class="b_algo">
        <h2><a href="https://example.org/report">GLP-1 药物经济学报告</a></h2>
        <p>来自公开网页的摘要内容。</p>
      </li>
    </body></html>
    """

    results = agent_module._parse_search_html(html, query="GLP-1 药物经济学", source="bing", max_results=3)

    assert results == [
        {
            "title": "GLP-1 药物经济学报告",
            "url": "https://example.org/report",
            "snippet": "来自公开网页的摘要内容。",
            "query": "GLP-1 药物经济学",
            "source": "bing",
        }
    ]


def test_web_fetch_cleans_html_content(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)

    class FakeResponse:
        text = """
        <html><head><title>测试页面</title><style>.x{}</style></head>
        <body><script>alert(1)</script><main><h1>标题</h1><p>正文 内容</p></main></body></html>
        """

        def raise_for_status(self):
            return None

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(agent_module.httpx, "AsyncClient", FakeClient)

    fetched = asyncio.run(agent_module._web_fetch("https://example.org/report"))

    assert fetched["title"] == "测试页面"
    assert fetched["status"] == "fetched"
    assert "正文 内容" in fetched["content"]
    assert "alert" not in fetched["content"]
    assert ".x" not in fetched["content"]


def test_resume_continues_after_checkpoint_without_replaying_prior_stages(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    runner = make_runner(agent_module)
    checkpoint_id, framework_ref = make_langgraph_checkpoint(
        agent_module,
        runner,
        session_id="sess-resume",
        run_id="run-resume",
        stage_count=4,
    )

    events = collect_stream(
        runner,
        {
            "session_id": "sess-resume",
            "invocation_id": "resume-1",
            "checkpoint_resume": True,
            "run_id": "run-resume",
            "checkpoint_id": checkpoint_id,
            "framework_ref": framework_ref,
        },
    )

    checkpoint_stages = [
        event["metadata"]["agentengine"]["stage"]
        for event in events
        if event["type"] == "checkpoint"
    ]
    assert checkpoint_stages == ["交叉分析发现", "批判性质检", "生成研究报告"]
    final_output = events[-1]["output"]
    assert "已完成阶段直接跳过：规划研究问题、检索公开网页、抓取来源正文、筛选证据并去重" in final_output
    assert "`deepresearch:plan:v1`" in final_output
    assert "`deepresearch:evidence_screen:v1`" in final_output
    assert "没有重复执行 checkpoint 前的副作用工具" in final_output
    assert "LangGraph 子图和多 Agent" in final_output


def test_resume_summary_matches_selected_checkpoint(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    runner = make_runner(agent_module)
    checkpoint_id, framework_ref = make_langgraph_checkpoint(
        agent_module,
        runner,
        session_id="sess-resume-first",
        run_id="run-resume-first",
        stage_count=1,
    )

    events = collect_stream(
        runner,
        {
            "session_id": "sess-resume-first",
            "invocation_id": "resume-first-1",
            "checkpoint_resume": True,
            "run_id": "run-resume-first",
            "checkpoint_id": checkpoint_id,
            "framework_ref": framework_ref,
        },
    )

    checkpoint_stages = [
        event["metadata"]["agentengine"]["stage"]
        for event in events
        if event["type"] == "checkpoint"
    ]
    assert checkpoint_stages == ["检索公开网页", "抓取来源正文", "筛选证据并去重", "交叉分析发现", "批判性质检", "生成研究报告"]
    final_output = events[-1]["output"]
    assert "已完成阶段直接跳过：规划研究问题。" in final_output
    assert "本次继续执行阶段：检索公开网页、抓取来源正文、筛选证据并去重、交叉分析发现、批判性质检、生成研究报告。" in final_output
    assert "已复用 tool receipt：`deepresearch:plan:v1`" in final_output
    assert "`deepresearch:web_search:v1`，没有重复" not in final_output


def test_resume_stream_uses_langgraph_checkpoint_config(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    runner = make_runner(agent_module)
    stage_keys = [stage.key for stage in agent_module.REPORT_STAGES]
    checkpoint_config = {
        "configurable": {
            "thread_id": "tenant:agent:sess-resume:run-resume",
            "checkpoint_ns": "",
            "checkpoint_id": "ckpt-after-aggregate",
        }
    }
    stream_calls: list[dict[str, Any]] = []

    class FakeGraph:
        def __init__(self):
            self.state: dict[str, Any] = {
                "completed_stage_keys": stage_keys[:2],
                "stage_summaries": [],
                "tool_receipts": [],
            }
            self.counter = 2

        async def astream(self, graph_input, *, config=None, context=None, stream_mode=None):
            stream_calls.append(
                {
                    "graph_input": graph_input,
                    "config": config,
                    "context": context,
                    "stream_mode": stream_mode,
                }
            )
            for stage in agent_module.REPORT_STAGES[2:]:
                self.counter += 1
                self.state = agent_module._run_stage(self.state, stage)
                yield {stage.key: dict(self.state)}
            self.state = {**self.state, "answer": "graph-final-answer"}
            yield {"finalize_report": {"answer": "graph-final-answer"}}

        async def aget_state(self, config):
            del config
            return SimpleNamespace(
                values=dict(self.state),
                config={
                    "configurable": {
                        "thread_id": "tenant:agent:sess-resume:run-resume",
                        "checkpoint_ns": "",
                        "checkpoint_id": f"ckpt-after-{self.counter}",
                    }
                },
            )

    fake_graph = FakeGraph()

    async def fake_build_execution_graph():
        return fake_graph, None

    async def fake_resolve_resume_state(graph, *, payload, session_id):
        assert graph is fake_graph
        assert session_id == "sess-resume"
        assert payload["checkpoint_id"] == "ckpt-after-aggregate"
        return checkpoint_config, 2, stage_keys[:2]

    async def fail_if_manual_step_loop(*_args, **_kwargs):
        raise AssertionError("checkpoint resume must use graph.astream(None, checkpoint_config)")

    monkeypatch.setattr(runner, "_build_execution_graph", fake_build_execution_graph)
    monkeypatch.setattr(runner, "_resolve_resume_state", fake_resolve_resume_state)
    monkeypatch.setattr(runner, "_invoke_graph_step", fail_if_manual_step_loop)

    events = collect_stream(
        runner,
        {
            "session_id": "sess-resume",
            "invocation_id": "resume-1",
            "checkpoint_resume": True,
            "run_id": "run-resume",
            "checkpoint_id": "ckpt-after-aggregate",
            "framework_ref": {
                "langgraph": {
                    "thread_id": "tenant:agent:sess-resume:run-resume",
                    "checkpoint_ns": "",
                    "checkpoint_id": "ckpt-after-aggregate",
                }
            },
        },
    )

    assert stream_calls == [
        {
            "graph_input": None,
            "config": checkpoint_config,
            "context": None,
            "stream_mode": "updates",
        }
    ]
    assert [
        event["metadata"]["agentengine"]["stage"]
        for event in events
        if event["type"] == "checkpoint"
    ] == ["抓取来源正文", "筛选证据并去重", "交叉分析发现", "批判性质检", "生成研究报告"]
    assert events[-1]["type"] == "final"
    assert "已完成阶段直接跳过：规划研究问题、检索公开网页" in events[-1]["output"]


def test_thread_config_keeps_checkpoint_namespace_but_drops_checkpoint_id(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)

    config = agent_module.LongTaskE2ERunner._thread_config_from(
        {
            "configurable": {
                "thread_id": "tenant:agent:sess:run",
                "checkpoint_ns": "subgraph-ns",
                "checkpoint_id": "ckpt-old",
            }
        }
    )

    assert config == {
        "configurable": {
            "thread_id": "tenant:agent:sess:run",
            "checkpoint_ns": "subgraph-ns",
        }
    }


def test_non_streaming_resume_does_not_emit_display_checkpoint_metadata(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    runner = make_runner(agent_module)
    checkpoint_id, framework_ref = make_langgraph_checkpoint(
        agent_module,
        runner,
        session_id="sess-invoke-resume",
        run_id="run-invoke-resume",
        stage_count=2,
    )

    result = asyncio.run(
        runner.invoke(
            {
                "session_id": "sess-invoke-resume",
                "invocation_id": "resume-invoke-1",
                "checkpoint_resume": True,
                "run_id": "run-invoke-resume",
                "checkpoint_id": checkpoint_id,
                "framework_ref": framework_ref,
            }
        )
    )

    assert "metadata" not in result
    assert "Deep Research" in result["output"]
    assert "通用 DeepResearch" not in result["output"]
