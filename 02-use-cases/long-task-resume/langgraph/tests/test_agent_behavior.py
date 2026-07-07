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


def patch_llm(monkeypatch: Any, agent_module: Any):
    async def fake_call_chat_model(messages, *, temperature=0.2):
        del temperature
        prompt = messages[-1]["content"]
        if "请只输出 JSON" in prompt:
            return """{
              "topic": "LLM 生成的 GLP-1 研究计划",
              "objectives": ["评估临床证据和支付准入"],
              "sub_questions": ["疗效如何", "安全性如何", "准入障碍是什么"],
              "search_queries": ["GLP-1 obesity diabetes cardiovascular outcomes", "GLP-1 pharmacoeconomics payer access", "GLP-1 real world safety"],
              "evidence_criteria": ["优先系统综述、RCT、真实世界研究"],
              "report_outline": ["摘要", "证据", "风险", "建议"]
            }"""
        if "请输出 JSON 数组" in prompt:
            return """[
              {
                "title": "LLM 筛选证据",
                "url": "https://example.org/glp1",
                "category": "临床证据",
                "relevance": "high",
                "evidence_level": "moderate",
                "key_finding": "GLP-1 药物在体重和糖代谢终点上均有证据支持。",
                "limitations": "需要核对具体适应症和人群外推。"
              }
            ]"""
        if "独立医学研究审稿人" in prompt:
            return "LLM 质检：证据覆盖仍需补充真实世界安全性和支付准入资料。"
        if "请写一份面向医药业务和技术团队" in prompt:
            return "# LLM 生成的 Deep Research 报告\n\n基于证据表和质检意见形成谨慎结论。"
        if "生成一份可直接在浏览器打开的自包含 HTML" in prompt:
            return "<!doctype html><html><head><title>Deep Research</title></head><body><h1>LLM 生成的 Deep Research 报告</h1></body></html>"
        if "刚完成的研究阶段" in prompt:
            return "LLM 阶段进度：本阶段已经完成，相关产物已保存，下一步继续推进后续研究。"
        if "已经开始真实 Deep Research" in prompt:
            return "LLM 启动确认：我会围绕该问题开始检索、阅读和分析，并持续更新阶段进度。"
        return "LLM 分析输出：基于当前证据形成阶段性判断。"

    async def fake_stream_chat_model(messages, *, temperature=0.2):
        del messages, temperature
        for chunk in ["LLM 正在启动真实 Deep Research，", "我会先确认研究问题并开始检索。"]:
            yield chunk

    monkeypatch.setattr(agent_module, "_call_chat_model", fake_call_chat_model)
    monkeypatch.setattr(agent_module, "_stream_chat_model", fake_stream_chat_model)


async def run_stage(agent_module: Any, state: dict[str, Any], stage: Any) -> dict[str, Any]:
    if stage.key == "plan_research":
        return await agent_module._run_plan_research_stage(state, stage)
    if stage.key == "search_web":
        return await agent_module._run_web_search_stage(state, stage)
    if stage.key == "fetch_sources":
        return await agent_module._run_fetch_sources_stage(state, stage)
    if stage.key == "screen_evidence":
        return await agent_module._run_screen_evidence_stage(state, stage)
    if stage.key == "analyze_findings":
        return await agent_module._run_analysis_stage(state, stage)
    if stage.key == "critic_review":
        return await agent_module._run_critic_stage(state, stage)
    if stage.key == "write_report":
        return await agent_module._run_write_report_stage(state, stage)
    raise AssertionError(f"unexpected stage {stage.key}")


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
    patch_llm(monkeypatch, agent_module)

    events = collect_stream(
        make_runner(agent_module),
        {
            "session_id": "sess-long",
            "invocation_id": "launch-1",
            "input": "调研 GLP-1 受体激动剂在肥胖和 2 型糖尿病治疗中的临床证据、药物经济学、支付准入和真实世界安全性",
        },
    )

    assert [event["type"] for event in events] == ["text", "text", "final"]
    assert events[-1]["output"] == "".join(event["delta"] for event in events if event["type"] == "text")
    assert events[-1]["output"] == "LLM 正在启动真实 Deep Research，我会先确认研究问题并开始检索。"
    assert "研究主题" not in events[-1]["output"]
    assert "成熟深度研究 Agent" not in events[-1]["output"]
    assert "web_search 子图" not in events[-1]["output"]
    assert "run_id" not in events[-1]["output"]
    assert "invocation_id" not in events[-1]["output"]
    assert "checkpoint" not in events[-1]["output"]
    assert "LangGraph" not in events[-1]["output"]
    assert "模拟一次外部工具失败" not in events[-1]["output"]
    assert not any(event["type"] == "checkpoint" for event in events)


def test_non_streaming_research_question_starts_research_without_internal_report(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    patch_llm(monkeypatch, agent_module)
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
    assert "LLM 启动确认" in output
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
    # ksadk 内置 web_fetch 未配置时返回 None，走 fallback httpx 路径验证 HTML 清洗
    async def _fake_ksadk_fetch(url):
        return None
    monkeypatch.setattr(agent_module, "_fetch_with_ksadk_web_fetch", _fake_ksadk_fetch)

    fetched = asyncio.run(agent_module._web_fetch("https://example.org/report"))

    assert fetched["title"] == "测试页面"
    assert fetched["status"] == "fetched"
    assert "正文 内容" in fetched["content"]
    assert "alert" not in fetched["content"]
    assert ".x" not in fetched["content"]


def test_research_stages_emit_multi_tool_events(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    patch_llm(monkeypatch, agent_module)

    async def fake_web_search(query: str, *, max_results: int = 5):
        return [
            {
                "title": f"Source for {query}",
                "url": f"https://example.org/{query.replace(' ', '-')}",
                "snippet": f"Snippet for {query}",
                "query": query,
                "source": "fixture",
            }
        ]

    monkeypatch.setattr(agent_module, "_web_search", fake_web_search)

    state = agent_module._initial_state(
        {"input": "调研 GLP-1 受体激动剂在肥胖和 2 型糖尿病治疗中的临床证据、药物经济学、支付准入和真实世界安全性"}
    )
    plan_stage = agent_module._stage_by_key("plan_research")
    state.update(asyncio.run(agent_module._run_plan_research_stage(state, plan_stage)))

    search_stage = agent_module._stage_by_key("search_web")
    search_update = asyncio.run(agent_module._run_web_search_stage(state, search_stage))

    stage_events = search_update.get("stage_events")
    assert isinstance(stage_events, list)
    tool_calls = [event for event in stage_events if event.get("type") == "tool_call"]
    assert len(tool_calls) >= 3
    assert any(event.get("tool_name") == "deepresearch_query_agent" for event in tool_calls)
    assert any(event.get("tool_name") == "deepresearch_gap_checker" for event in tool_calls)


def test_report_stage_writes_markdown_and_html_to_builtin_workspace(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    patch_llm(monkeypatch, agent_module)
    state = {
        **agent_module._initial_state({"input": "调研 GLP-1 药物经济学和支付准入"}),
        "evidence_table": [
            {
                "title": "GLP-1 Evidence",
                "url": "https://example.org/glp1",
                "category": "药物经济学",
                "key_finding": "成本效果和支付准入需要联合评估。",
            }
        ],
        "analysis_markdown": "### market_reviewer\n支付准入是核心不确定性。",
        "critic_markdown": "需要标注证据缺口。",
    }

    update = asyncio.run(agent_module._run_write_report_stage(state, agent_module._stage_by_key("write_report")))

    workspace_root = tmp_path / "ui" / "workspace"
    workspace_files = sorted(path.relative_to(workspace_root).as_posix() for path in workspace_root.rglob("*") if path.is_file())
    assert any(path.endswith("/deepresearch-report.md") for path in workspace_files)
    assert any(path.endswith("/deepresearch-report.html") for path in workspace_files)
    assert any(event.get("tool_name") == "write_workspace_files" for event in update["stage_events"])
    html_reports = [workspace_root / path for path in workspace_files if path.endswith("/deepresearch-report.html")]
    assert "<html" in html_reports[0].read_text(encoding="utf-8").lower()
    assert "LLM 生成的 Deep Research 报告" in html_reports[0].read_text(encoding="utf-8")


def test_background_cancel_accepts_foreground_invocation_and_run_id_alias(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    patch_llm(monkeypatch, agent_module)
    runner = make_runner(agent_module)

    async def noop(*args, **kwargs):
        return None

    monkeypatch.setattr(agent_module.conversation, "append_run_status_event", noop)
    monkeypatch.setattr(agent_module.conversation, "append_conversation_event", noop)

    async def _run() -> None:
        job_id = runner._start_background_long_task(
            {"input": "调研 GLP-1 药物经济学和支付准入"},
            "foreground-invoke-1",
            "sess-cancel-alias",
        )
        run_id = runner._background_runs_by_session["sess-cancel-alias"]
        try:
            assert runner.request_cancel("foreground-invoke-1") == "accepted"
            assert runner.request_cancel(run_id) == "accepted"
        finally:
            runner.request_cancel(job_id)
            task = runner._background_tasks.get(job_id)
            if task is not None:
                await asyncio.wait_for(task, timeout=5)

    asyncio.run(_run())


def test_resume_continues_after_checkpoint_without_replaying_prior_stages(monkeypatch: Any, tmp_path: Path):
    agent_module = load_agent(monkeypatch, tmp_path)
    patch_llm(monkeypatch, agent_module)
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
    patch_llm(monkeypatch, agent_module)
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
    patch_llm(monkeypatch, agent_module)
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
                self.state.update(await run_stage(agent_module, self.state, stage))
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
    patch_llm(monkeypatch, agent_module)
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
