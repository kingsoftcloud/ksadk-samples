from __future__ import annotations

import asyncio
import html
import json
import operator
import os
import re
import uuid
from dataclasses import dataclass
from hashlib import sha1
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from typing import Annotated, Any, AsyncIterator, TypedDict

import httpx
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

import ksadk.conversations as conversation
from ksadk.conversations.run_kinds import RUN_MODE_BACKGROUND, RUN_TRIGGER_NEW_RUN
from ksadk.runners.langgraph_runner import LangGraphRunner
from ksadk.sessions import resolve_session_service
from ksadk.toolsets.web import web_fetch as _ksadk_web_fetch
from ksadk.toolsets.web import web_search as _ksadk_web_search
from ksadk.toolsets.workspace import write_workspace_file, write_workspace_files
from stages import _artifact_path
from stages import *
from llm_client import _call_chat_model, _call_required_llm, _model_configured, _stream_chat_model
from search import _fetch_with_ksadk_web_fetch, _parse_search_html, _web_fetch, _web_search
from workflow import (
    _build_analysis_subgraph,
    _build_graph,
    _build_web_search_subgraph,
    _compile_graph,
    _expand_queries_for_gap,
    _extract_json_array,
    _extract_json_object,
    _fetch_all_sources,
    _json_dumps,
    _record_stage,
    _render_final_answer,
    _run_analysis_stage,
    _run_critic_stage,
    _run_fetch_sources_stage,
    _run_plan_research_stage,
    _run_screen_evidence_stage,
    _run_stage,
    _run_web_search_stage,
    _run_write_report_stage,
    _runtime_event_pair,
    _runtime_events_from_packets,
    _search_gap_summary,
    _stage_node,
    _workspace_write_events,
    _ensure_html_document,
    _dedupe_search_results,
    _fallback_expanded_queries,
    finalize_report,
)


def _stage_delay_seconds() -> float:
    raw = os.environ.get("LONG_TASK_STAGE_DELAY_SECONDS", "4")
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 4.0


def _fail_stage_key() -> str:
    return os.environ.get("LONG_TASK_FAIL_STAGE", "analyze_findings").strip()


def _should_fail_stage(stage: ReportStage, source: str) -> bool:
    return bool(_fail_stage_key()) and source == "start" and stage.key == _fail_stage_key()


def _is_long_task_intent(text: str) -> bool:
    normalized = str(text or "").lower()
    explicit_background = any(keyword in normalized for keyword in EXPLICIT_BACKGROUND_KEYWORDS) and any(
        keyword in normalized for keyword in EXPLICIT_START_KEYWORDS
    )
    research_request = any(keyword in normalized for keyword in RESEARCH_ACTION_KEYWORDS) and (
        len(normalized) >= 12 or any(keyword in normalized for keyword in GENERIC_RESEARCH_DOMAIN_HINTS)
    )
    return explicit_background or research_request


def _is_status_intent(text: str) -> bool:
    normalized = str(text or "").lower()
    return any(keyword in normalized for keyword in ("进度", "状态", "做到哪", "到哪", "后台任务"))


def _stage_by_key(stage_key: str) -> ReportStage:
    for stage in REPORT_STAGES:
        if stage.key == stage_key:
            return stage
    return REPORT_STAGES[0]


def _initial_state(payload: dict[str, Any]) -> ReportState:
    query = str(payload.get("input") or "").strip()
    default_query = "调研 GLP-1 受体激动剂在肥胖和 2 型糖尿病治疗中的临床证据、药物经济学、支付准入和真实世界安全性。"
    actual_query = query or default_query
    return {
        "input": actual_query,
        "task_title": f"Deep Research: {actual_query[:60]}",
        "completed_stage_keys": [],
        "stage_summaries": [],
        "tool_receipts": [],
        "stage_events": [],
        "subgraph_traces": [],
        "requires_critic_review": True,
    }


def ksadk_prepare_state(payload: dict[str, Any], session_context: dict[str, Any]) -> ReportState:
    del session_context
    return _initial_state(payload)


def _demo_mode() -> str:
    return os.environ.get("LONG_TASK_RESUME_DEMO_MODE", "fixture").strip().lower() or "fixture"


def _artifact_path_for_state(state: ReportState, stage: ReportStage) -> str:
    suffix = f"/{stage.artifact_name}"
    for path in list(state.get("workspace_artifacts") or []):
        value = str(path)
        if value.endswith(suffix) or value == stage.artifact_name:
            return value
    return str(_artifact_path(stage))


def _checkpoint_metadata_for_ref(
    *,
    stage: ReportStage,
    run_id: str,
    framework_ref: dict[str, Any],
    artifact_path: str | None = None,
) -> dict[str, Any]:
    display_artifact_path = artifact_path or str(_artifact_path(stage))
    # framework_ref.langgraph stores the LangGraph StateSnapshot config used by ResumeRun.
    return {
        "agentengine": {
            "run_id": run_id,
            "phase": stage.phase,
            "stage": stage.title,
            "summary": f"{stage.checkpoint_note} 产物：{display_artifact_path}",
            "next_action": _next_action_for_stage(stage),
            "status": "completed",
            "tool_name": stage.tool_name,
            "receipt_key": stage.receipt_key,
            "artifact_path": display_artifact_path,
            "framework": "langgraph",
            "framework_ref": framework_ref,
        }
    }


def _stage_for_completed_count(completed_count: int) -> ReportStage:
    if completed_count <= 0:
        return REPORT_STAGES[0]
    return REPORT_STAGES[min(completed_count - 1, len(REPORT_STAGES) - 1)]


def _next_action_for_stage(stage: ReportStage) -> str:
    for index, candidate in enumerate(REPORT_STAGES):
        if candidate.key != stage.key:
            continue
        if index + 1 >= len(REPORT_STAGES):
            return "任务已完成，无需再次恢复"
        return stage.next_action_detail
    return "继续执行后续业务阶段"


def _user_facing_stage_update(stage: ReportStage, artifact_path: Path) -> str:
    updates = {
        "plan_research": "我已经把问题拆成研究目标、关键子问题、检索关键词和报告结构。",
        "search_web": "我已经完成第一轮公开资料检索，并保留了候选来源，下一步会阅读原文。",
        "fetch_sources": "我已经阅读并清洗了候选来源正文，接下来会筛选真正可引用的证据。",
        "screen_evidence": "我已经完成证据筛选和去重，接下来进入交叉分析。",
        "analyze_findings": "我已经完成多角度分析，正在把事实、趋势、风险和不确定项分开。",
        "critic_review": "我已经完成反向质检，检查了引用覆盖、反例和推理跳跃。",
        "write_report": "研究报告已经生成，包含摘要、证据表、主要发现、风险提示和后续建议。",
    }
    next_action = _next_action_for_stage(stage)
    return f"{updates.get(stage.key, stage.checkpoint_note)}\n产物：`{artifact_path}`\n下一步：{next_action}。"


def _stage_index_from_snapshot_values(values: dict[str, Any]) -> int:
    completed = list(values.get("completed_stage_keys") or [])
    return min(len(completed), len(REPORT_STAGES))


def _research_launch_message(question: str) -> str:
    raise RuntimeError("Launch messages must be generated by the configured LLM")


class LongTaskE2ERunner(LangGraphRunner):
    def __init__(self, detection_result: Any, project_dir: str):
        super().__init__(detection_result, project_dir)
        self._module = None
        self._cancel_events: dict[str, asyncio.Event] = {}
        self._cancel_aliases: dict[str, str] = {}
        self._background_tasks: dict[str, asyncio.Task[Any]] = {}
        self._background_runs_by_session: dict[str, str] = {}
        self._fixture_graph = None

    def load_agent(self) -> None:
        self._agent = None
        self._module = None
        self._fixture_graph = None

    async def _with_graph(self, callback):
        graph, saver_cm = await _build_graph()
        previous_agent = self._agent
        previous_module = self._module
        self._agent = graph
        self._module = None
        try:
            return await callback()
        finally:
            self._agent = previous_agent
            self._module = previous_module
            await saver_cm.__aexit__(None, None, None)

    async def invoke(self, input_data: dict[str, Any]) -> dict[str, Any]:
        if _demo_mode() != "postgres":
            payload = dict(input_data)
            if not payload.get("checkpoint_resume") and _is_long_task_intent(str(payload.get("input") or "")):
                session_id = str(payload.get("session_id") or "local-session")
                invocation_id = str(payload.get("invocation_id") or uuid.uuid4().hex)
                self._start_background_long_task(payload, invocation_id, session_id)
                output = await _call_required_llm(
                    f"用户研究问题：{payload.get('input') or ''}\n请简短说明你已经开始真实 Deep Research，会继续检索、阅读和分析。不要提实现细节。",
                    system="你是医药 Deep Research 智能体。输出自然的启动确认。",
                    temperature=0.3,
                )
                return {"output": output, "raw": {"started": True}}
            if payload.get("checkpoint_resume"):
                completed = [stage.key for stage in REPORT_STAGES]
            else:
                completed = [stage.key for stage in REPORT_STAGES[:2]]
            state: ReportState = {
                **_initial_state(payload),
                "completed_stage_keys": completed,
                "stage_summaries": [
                    {
                        "stage": stage.title,
                        "phase": stage.phase,
                        "summary": stage.checkpoint_note,
                    }
                    for stage in REPORT_STAGES
                    if stage.key in completed
                ],
                "tool_receipts": [
                    {
                        "receipt_key": stage.receipt_key,
                        "tool_name": stage.tool_name,
                        "stage": stage.title,
                        "status": (
                            "skipped_duplicate"
                            if stage.key in {item.key for item in REPORT_STAGES[:4]} and payload.get("checkpoint_resume")
                            else "recorded"
                        ),
                        "summary": stage.checkpoint_note,
                    }
                    for stage in REPORT_STAGES
                    if stage.key in completed
                ],
            }
            return {"output": _render_final_answer(state), "raw": state}

        async def _invoke():
            payload = dict(input_data)
            session_id = str(payload.get("session_id") or uuid.uuid4().hex[:8])
            is_checkpoint_resume = bool(payload.get("checkpoint_resume"))
            config = self._get_config(session_id)
            if is_checkpoint_resume:
                checkpoint_ref = self._extract_langgraph_checkpoint_ref(payload)
                config = self._apply_checkpoint_resume_config(
                    config,
                    session_id=session_id,
                    checkpoint_ref=checkpoint_ref,
                )
                graph_input = None
            else:
                graph_input = _initial_state(payload)

            result = await self._invoke_graph(
                graph_input,
                config=config,
                context=self.build_native_context(payload.get("platform_context")),
            )
            output = {"output": self._extract_output(result), "raw": result}
            metadata = {} if is_checkpoint_resume else await self._latest_checkpoint_metadata(config)
            if metadata:
                output["metadata"] = metadata
            return output

        return await self._with_graph(_invoke)

    def _get_fixture_graph(self):
        if self._fixture_graph is None:
            self._fixture_graph = _compile_graph(InMemorySaver())
        return self._fixture_graph

    async def _build_execution_graph(self):
        if _demo_mode() == "postgres":
            graph, saver_cm = await _build_graph()
            return graph, saver_cm
        return self._get_fixture_graph(), None

    async def _invoke_graph_step(
        self,
        graph: Any,
        *,
        graph_input: ReportState | None,
        config: dict[str, Any],
        stage: ReportStage,
        payload: dict[str, Any],
    ) -> tuple[ReportState, dict[str, Any], str, dict[str, Any]]:
        await graph.ainvoke(
            graph_input,
            config=config,
            context=self.build_native_context(payload.get("platform_context")),
            interrupt_after=[stage.key],
        )
        latest_config = self._thread_config_from(config)
        snapshot = await graph.aget_state(latest_config)
        values = dict(getattr(snapshot, "values", {}) or {})
        checkpoint_ref = self._checkpoint_ref_from_state(snapshot)
        if not checkpoint_ref:
            raise RuntimeError(f"LangGraph did not return checkpoint ref after {stage.key}")
        checkpoint_id = str(checkpoint_ref["langgraph"]["checkpoint_id"])
        next_config = self._thread_config_from(getattr(snapshot, "config", None) or latest_config)
        return values, checkpoint_ref, checkpoint_id, next_config

    @staticmethod
    def _thread_config_from(config: dict[str, Any]) -> dict[str, Any]:
        configurable = dict((config or {}).get("configurable") or {})
        thread_id = str(configurable.get("thread_id") or "").strip()
        if not thread_id:
            return dict(config or {})
        checkpoint_ns = str(configurable.get("checkpoint_ns") or "").strip()
        # Reading the latest thread state must not keep checkpoint_id; LangGraph
        # otherwise returns the historical snapshot instead of the resumed state.
        next_configurable = {"thread_id": thread_id}
        if checkpoint_ns:
            next_configurable["checkpoint_ns"] = checkpoint_ns
        return {"configurable": next_configurable}

    async def _latest_thread_state(
        self,
        graph: Any,
        config: dict[str, Any],
    ) -> tuple[ReportState, dict[str, Any], str, dict[str, Any]]:
        thread_config = self._thread_config_from(config)
        snapshot = await graph.aget_state(thread_config)
        values = dict(getattr(snapshot, "values", {}) or {})
        framework_ref = self._checkpoint_ref_from_state(snapshot)
        if not framework_ref:
            raise RuntimeError("LangGraph did not return latest checkpoint ref")
        checkpoint_id = str(framework_ref["langgraph"]["checkpoint_id"])
        next_config = self._thread_config_from(getattr(snapshot, "config", None) or thread_config)
        return values, framework_ref, checkpoint_id, next_config

    @staticmethod
    def _stage_from_update(update: dict[str, Any]) -> ReportStage | None:
        for stage in REPORT_STAGES:
            if stage.key in update:
                return stage
        return None

    @staticmethod
    def _state_from_update(update: dict[str, Any]) -> ReportState:
        for stage in REPORT_STAGES:
            value = update.get(stage.key)
            if isinstance(value, dict):
                return dict(value)
        finalize = update.get("finalize_report")
        if isinstance(finalize, dict):
            return dict(finalize)
        return {}

    async def _resolve_resume_state(
        self,
        graph: Any,
        *,
        payload: dict[str, Any],
        session_id: str,
    ) -> tuple[dict[str, Any], int, list[str]]:
        checkpoint_ref = self._extract_langgraph_checkpoint_ref(payload)
        config = self._apply_checkpoint_resume_config(
            self._get_config(session_id),
            session_id=session_id,
            checkpoint_ref=checkpoint_ref,
        )
        snapshot = await graph.aget_state(config)
        values = dict(getattr(snapshot, "values", {}) or {})
        start_index = _stage_index_from_snapshot_values(values)
        completed_before = [stage.key for stage in REPORT_STAGES[:start_index]]
        return config, start_index, completed_before

    async def _cleanup_graph_context(self, saver_cm: Any) -> None:
        if saver_cm is not None:
            await saver_cm.__aexit__(None, None, None)

    async def stream(self, input_data: dict[str, Any]):
        payload = dict(input_data)
        invocation_id = str(payload.get("invocation_id") or payload.get("run_id") or uuid.uuid4().hex)
        session_id = str(payload.get("session_id") or "local-session")
        user_input = str(payload.get("input") or "")

        if payload.get("checkpoint_resume"):
            async for event in self._stream_checkpoint_resume(payload, invocation_id, session_id):
                yield event
            return

        if _is_status_intent(user_input):
            output = await self._render_status_answer(session_id)
            yield {"type": "text", "delta": output}
            yield {"type": "final", "output": output}
            return

        if _is_long_task_intent(user_input):
            self._start_background_long_task(payload, invocation_id, session_id)
            chunks: list[str] = []
            try:
                async for chunk in self._stream_research_launch_message(user_input):
                    chunks.append(chunk)
                    yield {"type": "text", "delta": chunk}
            except Exception as exc:
                output = f"真实 LLM 启动回复失败：{type(exc).__name__}: {exc}"
                yield {"type": "text", "delta": output}
                yield {"type": "final", "output": output}
                return
            output = "".join(chunks).strip()
            yield {"type": "final", "output": output}
            return

        output = await self._chat_with_model(payload)
        yield {"type": "text", "delta": output}
        yield {"type": "final", "output": output}

    async def _chat_with_model(self, payload: dict[str, Any]) -> str:
        user_input = str(payload.get("input") or "").strip()
        if not _model_configured():
            return (
                "模型未配置：普通对话不会伪造成长任务恢复结果。请在 `.env` 中配置 "
                "`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL_NAME` 后再重试。"
            )

        base_url = os.environ["OPENAI_BASE_URL"].rstrip("/")
        api_key = os.environ["OPENAI_API_KEY"]
        model = os.environ["OPENAI_MODEL_NAME"]
        history = payload.get("history")
        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "你是一个用于长任务恢复 E2E 演示的助手。普通聊天要正常回答；"
                    "不要在普通聊天里声称已经创建 checkpoint。"
                ),
            }
        ]
        if isinstance(history, list):
            for item in history[-8:]:
                if not isinstance(item, dict):
                    continue
                role = str(item.get("role") or "").strip()
                content = str(item.get("content") or item.get("text") or "").strip()
                if role in {"user", "assistant", "system"} and content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_input or "你好"})

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": model, "messages": messages, "stream": False},
                )
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            return f"普通 LLM 对话调用失败：{type(exc).__name__}: {exc}"

        choices = data.get("choices") if isinstance(data, dict) else None
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") if isinstance(choices[0], dict) else None
            content = message.get("content") if isinstance(message, dict) else None
            if content:
                return str(content)
        return "模型已返回，但响应中没有可展示文本。"

    def _start_background_long_task(self, payload: dict[str, Any], invocation_id: str, session_id: str) -> str:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        job_invocation_id = f"longtask_{run_id}"
        self._background_runs_by_session[session_id] = run_id
        cancel_event = asyncio.Event()
        self._cancel_events[job_invocation_id] = cancel_event
        for alias in {job_invocation_id, invocation_id, run_id}:
            if alias:
                self._cancel_aliases[str(alias)] = job_invocation_id
        task = asyncio.create_task(
            self._run_background_job(
                payload=payload,
                session_id=session_id,
                run_id=run_id,
                invocation_id=job_invocation_id,
                start_index=0,
                cancel_event=cancel_event,
                source="start",
            )
        )
        self._background_tasks[job_invocation_id] = task
        task.add_done_callback(lambda _task: self._background_tasks.pop(job_invocation_id, None))
        return job_invocation_id

    async def _stream_research_launch_message(self, question: str) -> AsyncIterator[str]:
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个真实执行 Deep Research 的医药研究智能体。"
                    "用户发起长任务后，你需要自然确认理解、简述研究切入点和接下来会启动的真实检索、阅读、分析流程。"
                    "不要说你已经完成任何还没完成的步骤；不要使用固定模板；不要提 checkpoint、run_id、LangGraph。"
                ),
            },
            {"role": "user", "content": question},
        ]
        async for chunk in _stream_chat_model(messages, temperature=0.3):
            yield chunk

    async def _generate_background_start_note(self, question: str) -> str:
        return await _call_required_llm(
            f"用户研究问题：{question}\n请用一句自然的话说明研究任务已经进入后台执行，会继续检索、阅读和分析。不要提实现细节。",
            system="你是医药 Deep Research 智能体。输出给普通用户看的简短进度说明。",
            temperature=0.3,
        )

    async def _generate_stage_update(self, state: ReportState, stage: ReportStage, artifact_path: Path) -> str:
        return await _call_required_llm(
            f"""
用户研究问题：
{state.get("input", "")}

刚完成的研究阶段：{stage.title}
阶段产物路径：{artifact_path}
阶段状态摘要：{state.get("stage_summaries", [])[-1] if state.get("stage_summaries") else ""}
下一步：{_next_action_for_stage(stage)}

请写一段自然的阶段进度更新。要求：
- 像真实研究助理汇报进度，不要使用固定模板。
- 可以提到已经保存了产物路径。
- 不要提 checkpoint、LangGraph、run_id。
- 不要夸大已经完成的内容。
""",
            system="你是医药 Deep Research 智能体。输出用户可读的进度更新。",
            temperature=0.25,
        )

    async def _render_status_answer(self, session_id: str) -> str:
        run_id = self._background_runs_by_session.get(session_id)
        if not run_id:
            return "当前会话里还没有正在进行的研究任务。你可以直接发一个研究问题，我会开始检索和整理资料。"
        service = resolve_session_service()
        events = await service.get_events(session_id)
        checkpoints = [
            event
            for event in events
            if event.event_type == "run_checkpoint"
            and str((event.metadata or {}).get("run_id") or "") == run_id
        ]
        latest = checkpoints[-1] if checkpoints else None
        if latest is None:
            return "研究刚开始，我正在拆解问题并准备第一批检索关键词。"
        metadata = latest.metadata or {}
        stage = metadata.get("stage") or metadata.get("phase") or "研究中"
        summary = str(metadata.get("summary") or "").replace("恢复后", "接下来")
        next_action = str(metadata.get("next_action") or "继续后续研究")
        return (
            f"当前进度：{stage}。\n"
            f"{summary}\n"
            f"下一步：{next_action}。"
        ).strip()

    @staticmethod
    def _stage_runtime_events(values: ReportState, *, stage: ReportStage, run_id: str) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for raw_event in list(values.get("stage_events") or []):
            if not isinstance(raw_event, dict):
                continue
            event_type = str(raw_event.get("type") or "").strip()
            if event_type not in {"tool_call", "tool_result"}:
                continue
            tool_name = str(raw_event.get("tool_name") or stage.tool_name)
            tool_args = {"stage": stage.key, **dict(raw_event.get("tool_args") or {})}
            event = {
                "type": event_type,
                "tool_name": tool_name,
                "tool_args": tool_args,
                "run_id": run_id,
                "text": str(raw_event.get("text") or tool_name),
            }
            if event_type == "tool_result":
                event["tool_output"] = dict(raw_event.get("tool_output") or {"ok": True})
            normalized.append(event)
        return normalized

    async def _append_runtime_stage_events(
        self,
        *,
        values: ReportState,
        stage: ReportStage,
        session_id: str,
        author: str,
        invocation_id: str,
        run_id: str,
    ) -> None:
        for event in self._stage_runtime_events(values, stage=stage, run_id=run_id):
            metadata: dict[str, Any] = {
                "tool_name": event["tool_name"],
                "tool_args": event["tool_args"],
                "run_id": run_id,
                "stage": stage.key,
                "background": True,
            }
            if event["type"] == "tool_result":
                metadata["tool_output"] = event.get("tool_output") or {"ok": True}
            await conversation.append_conversation_event(
                session_id=session_id,
                author=author,
                role="model" if event["type"] == "tool_call" else "user",
                text=str(event.get("text") or event["tool_name"]),
                invocation_id=invocation_id,
                event_type=event["type"],
                metadata=metadata,
                session_service_provider=resolve_session_service,
            )

    async def _stream_checkpoint_resume(
        self,
        payload: dict[str, Any],
        invocation_id: str,
        session_id: str,
    ):
        run_id = str(payload.get("run_id") or invocation_id)
        checkpoint_id = str(payload.get("checkpoint_id") or "")
        graph = None
        saver_cm = None
        try:
            graph, saver_cm = await self._build_execution_graph()
            config, start_index, completed_before = await self._resolve_resume_state(
                graph,
                payload=payload,
                session_id=session_id,
            )
        except Exception as exc:
            yield {
                "type": "final",
                "output": (
                    f"无法从 checkpoint `{checkpoint_id or 'latest'}` 恢复 `{run_id}`："
                    f"{type(exc).__name__}: {exc}"
                ),
            }
            await self._cleanup_graph_context(saver_cm)
            return

        yield {
            "type": "text",
            "delta": (
                "我会从上次已经完成的研究进度继续。\n"
                "已完成的检索、阅读和证据整理不会重复执行，接下来只补后续分析和报告。\n\n"
            ),
        }

        state: ReportState = {}
        try:
            async for update in graph.astream(
                None,
                config=config,
                context=self.build_native_context(payload.get("platform_context")),
                stream_mode="updates",
            ):
                if not isinstance(update, dict):
                    continue
                stage = self._stage_from_update(update)
                if stage is None:
                    update_state = self._state_from_update(update)
                    if update_state:
                        state.update(update_state)
                    continue

                yield {
                    "type": "tool_call",
                    "tool_name": stage.tool_name,
                    "tool_args": {"stage": stage.key, "resumed_from": checkpoint_id},
                    "run_id": run_id,
                }
                update_state = self._state_from_update(update)
                if update_state:
                    state.update(update_state)
                    if completed_before:
                        state["resumed_completed_stage_keys"] = list(completed_before)
                values, framework_ref, next_checkpoint_id, config = await self._latest_thread_state(
                    graph,
                    config=config,
                )
                state = {
                    **values,
                    "resumed_completed_stage_keys": list(completed_before),
                }
                artifact_path = _artifact_path_for_state(values, stage)
                for runtime_event in self._stage_runtime_events(state, stage=stage, run_id=run_id):
                    yield runtime_event
                yield {
                    "type": "tool_result",
                    "tool_name": stage.tool_name,
                    "tool_args": {"stage": stage.key, "resumed_from": checkpoint_id},
                    "tool_output": {
                        "ok": True,
                        "receipt_key": stage.receipt_key,
                        "artifact_path": artifact_path,
                        "resumed_from": checkpoint_id,
                    },
                    "run_id": run_id,
                }
                yield {
                    "type": "checkpoint",
                    "metadata": _checkpoint_metadata_for_ref(
                        stage=stage,
                        run_id=run_id,
                        framework_ref=framework_ref,
                        artifact_path=artifact_path,
                    ),
                }
                yield {
                    "type": "text",
                    "delta": (
                        f"**{stage.title}已完成**\n"
                        f"{_user_facing_stage_update(stage, Path(artifact_path))}\n\n"
                    ),
                }
                await asyncio.sleep(_stage_delay_seconds())

            final_state: ReportState = dict(state or {})
            if completed_before:
                final_state["resumed_completed_stage_keys"] = list(completed_before)
            if completed_before:
                final_state["tool_receipts"] = [
                    {
                        **receipt,
                        "status": (
                            "skipped_duplicate"
                            if receipt.get("receipt_key")
                            in {stage.receipt_key for stage in REPORT_STAGES[:start_index]}
                            else receipt.get("status", "recorded")
                        ),
                    }
                    for receipt in list(final_state.get("tool_receipts") or [])
                ]
            output_text = (
                _render_final_answer(final_state)
                if completed_before
                else str(final_state.get("answer") or "") or _render_final_answer(final_state)
            )
            yield {"type": "final", "output": output_text}
        finally:
            await self._cleanup_graph_context(saver_cm)
            self._cancel_events.pop(invocation_id, None)

    async def _run_background_job(
        self,
        *,
        payload: dict[str, Any],
        session_id: str,
        run_id: str,
        invocation_id: str,
        start_index: int,
        cancel_event: asyncio.Event,
        source: str,
    ) -> None:
        author = self.detection_result.name
        graph = None
        saver_cm = None
        await conversation.append_run_status_event(
            session_id=session_id,
            author=author,
            status="in_progress",
            invocation_id=invocation_id,
            detail=f"{source}:background_long_task_started:{run_id}",
            session_service_provider=resolve_session_service,
            run_mode=RUN_MODE_BACKGROUND,
            run_trigger=RUN_TRIGGER_NEW_RUN,
        )
        await conversation.append_conversation_event(
            session_id=session_id,
            author=author,
            role="model",
            text=await self._generate_background_start_note(str(payload.get("input") or "")),
            invocation_id=invocation_id,
            event_type="assistant_message",
            metadata={"run_id": run_id, "background": True},
            session_service_provider=resolve_session_service,
        )

        try:
            graph, saver_cm = await self._build_execution_graph()
            graph_config = self._get_config(f"{session_id}:{run_id}")
            graph_input: ReportState | None = _initial_state(payload)
            for stage in REPORT_STAGES[start_index:]:
                if cancel_event.is_set():
                    await self._append_cancelled(session_id, author, invocation_id, run_id)
                    return
                await conversation.append_conversation_event(
                    session_id=session_id,
                    author=author,
                    role="model",
                    text=stage.tool_name,
                    invocation_id=invocation_id,
                    event_type="tool_call",
                    metadata={
                        "tool_name": stage.tool_name,
                        "tool_args": {"stage": stage.key, "run_id": run_id},
                        "run_id": run_id,
                    },
                    session_service_provider=resolve_session_service,
                )
                await asyncio.sleep(_stage_delay_seconds())
                if cancel_event.is_set():
                    await self._append_cancelled(session_id, author, invocation_id, run_id)
                    return

                if _should_fail_stage(stage, source):
                    await conversation.append_conversation_event(
                        session_id=session_id,
                        author=author,
                        role="model",
                        text=(
                            f"{stage.title}暂时中断：外部资料或模型服务短暂不可用。"
                            "我已经保留了前面的研究进度，稍后可以从这里继续。"
                        ),
                        invocation_id=invocation_id,
                        event_type="assistant_message",
                        metadata={
                            "run_id": run_id,
                            "stage": stage.key,
                            "background": True,
                            "failed": True,
                        },
                        session_service_provider=resolve_session_service,
                    )
                    await conversation.append_run_status_event(
                        session_id=session_id,
                        author=author,
                        status="failed",
                        invocation_id=invocation_id,
                        detail=f"simulated_tool_failure:{stage.key}",
                        session_service_provider=resolve_session_service,
                        run_mode=RUN_MODE_BACKGROUND,
                        run_trigger=RUN_TRIGGER_NEW_RUN,
                    )
                    return

                values, framework_ref, checkpoint_id, graph_config = await self._invoke_graph_step(
                    graph,
                    graph_input=graph_input,
                    config=graph_config,
                    stage=stage,
                    payload=payload,
                )
                graph_input = None
                artifact_path = _artifact_path_for_state(values, stage)
                await self._append_runtime_stage_events(
                    values=values,
                    stage=stage,
                    session_id=session_id,
                    author=author,
                    invocation_id=invocation_id,
                    run_id=run_id,
                )
                await conversation.append_conversation_event(
                    session_id=session_id,
                    author=author,
                    role="user",
                    text=stage.stream_line,
                    invocation_id=invocation_id,
                    event_type="tool_result",
                    metadata={
                        "tool_name": stage.tool_name,
                        "tool_args": {"stage": stage.key, "run_id": run_id},
                        "tool_output": {
                            "ok": True,
                            "receipt_key": stage.receipt_key,
                            "artifact_path": artifact_path,
                            "langgraph_checkpoint_id": checkpoint_id,
                        },
                        "run_id": run_id,
                        "tool_receipt": self._tool_receipt_metadata_for_stage(
                            session_id=session_id,
                            run_id=run_id,
                            stage=stage,
                            checkpoint_id=checkpoint_id,
                            framework_ref=framework_ref,
                        ),
                    },
                    session_service_provider=resolve_session_service,
                )
                await conversation.append_run_checkpoint_event(
                    session_id=session_id,
                    author=author,
                    run_id=run_id,
                    checkpoint_id=checkpoint_id,
                    framework="langgraph",
                    framework_ref=framework_ref,
                    phase=stage.phase,
                    invocation_id=invocation_id,
                    metadata={
                        "stage": stage.title,
                        "summary": f"{stage.checkpoint_note} 产物：{artifact_path}",
                        "next_action": _next_action_for_stage(stage),
                        "status": "completed",
                        "tool_name": stage.tool_name,
                        "receipt_key": stage.receipt_key,
                        "artifact_path": artifact_path,
                    },
                    session_service_provider=resolve_session_service,
                )
                await conversation.append_conversation_event(
                    session_id=session_id,
                    author=author,
                    role="model",
                    text=await self._generate_stage_update(dict(values), stage, Path(artifact_path)),
                    invocation_id=invocation_id,
                    event_type="assistant_message",
                    metadata={
                        "run_id": run_id,
                        "stage": stage.key,
                        "background": True,
                    },
                    session_service_provider=resolve_session_service,
                )

            await conversation.append_run_status_event(
                session_id=session_id,
                author=author,
                status="completed",
                invocation_id=invocation_id,
                detail=f"background_long_task_completed:{run_id}",
                session_service_provider=resolve_session_service,
                run_mode=RUN_MODE_BACKGROUND,
                run_trigger=RUN_TRIGGER_NEW_RUN,
            )
        except asyncio.CancelledError:
            await self._append_cancelled(session_id, author, invocation_id, run_id)
            raise
        except Exception as exc:
            await conversation.append_run_status_event(
                session_id=session_id,
                author=author,
                status="failed",
                invocation_id=invocation_id,
                detail=str(exc),
                session_service_provider=resolve_session_service,
                run_mode=RUN_MODE_BACKGROUND,
                run_trigger=RUN_TRIGGER_NEW_RUN,
            )
        finally:
            await self._cleanup_graph_context(saver_cm)
            self._cancel_events.pop(invocation_id, None)
            aliases_to_delete = [alias for alias, target in self._cancel_aliases.items() if target == invocation_id]
            for alias in aliases_to_delete:
                self._cancel_aliases.pop(alias, None)

    async def _append_cancelled(self, session_id: str, author: str, invocation_id: str, run_id: str) -> None:
        await conversation.append_conversation_event(
            session_id=session_id,
            author=author,
            role="model",
            text="已暂停这次研究，并保留当前进度。后面可以从已完成的阶段继续。",
            invocation_id=invocation_id,
            event_type="assistant_message",
            metadata={"run_id": run_id, "background": True, "cancelled": True},
            session_service_provider=resolve_session_service,
        )
        await conversation.append_run_status_event(
            session_id=session_id,
            author=author,
            status="cancelled",
            invocation_id=invocation_id,
            detail="cancel_requested",
            session_service_provider=resolve_session_service,
            run_mode=RUN_MODE_BACKGROUND,
            run_trigger=RUN_TRIGGER_NEW_RUN,
        )

    def _tool_receipt_metadata_for_stage(
        self,
        *,
        session_id: str,
        run_id: str,
        stage: ReportStage,
        checkpoint_id: str,
        framework_ref: dict[str, Any],
        replayed: bool = False,
    ) -> dict[str, Any]:
        receipt_id = f"tr_{stage.receipt_key.replace(':', '_')}"
        return {
            "receipt_id": receipt_id,
            "idempotency_key": f"tool_receipt:{session_id}:{run_id}:{stage.receipt_key}",
            "tool_name": stage.tool_name,
            "tool_call_id": f"{run_id}:{stage.key}",
            "run_id": run_id,
            "checkpoint_id": checkpoint_id,
            "framework": "langgraph",
            "framework_ref": framework_ref,
            "status": "completed",
            "replayed": replayed,
        }

    def request_cancel(self, invocation_id: str) -> str:
        requested = str(invocation_id)
        canonical_invocation_id = self._cancel_aliases.get(requested, requested)
        event = self._cancel_events.get(canonical_invocation_id)
        if event is None:
            return "not_found"
        event.set()
        return "accepted"


root_agent = None
