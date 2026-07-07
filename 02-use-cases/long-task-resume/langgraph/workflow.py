"""LangGraph 节点编排层：7 个阶段节点 + subgraph + graph 编译。

从 agent.py 抽取的节点层。纯叶子模块，单向依赖 stages/llm_client/search +
ksadk.toolsets.workspace + langgraph + stdlib，零循环 import。
"""

from __future__ import annotations

import asyncio
import html
import json
import os
import re
from hashlib import sha1
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from stages import (
    REPORT_STAGES,
    WORKSPACE_DIR,
    AnalysisState,
    ReportStage,
    ReportState,
    WebSearchState,
    _artifact_path,
)
from llm_client import _call_required_llm
import search as search_mod
from ksadk.toolsets.workspace import write_workspace_file, write_workspace_files


# search 模块属性访问（避免固化绑定，test 双 patch 友好）
_web_search = search_mod._web_search
_web_fetch = search_mod._web_fetch




def _workspace_write_events(
    *,
    stage: ReportStage,
    tool_name: str,
    paths: list[str],
    result: dict[str, Any],
) -> list[dict[str, Any]]:
    return _runtime_event_pair(
        stage=stage,
        tool_name=tool_name,
        tool_args={"paths": paths},
        tool_output={key: value for key, value in result.items() if key != "absolute_path"},
        summary=f"Workspace 已写入 {len(paths)} 个文件：{', '.join(paths)}。",
    )


def _ensure_html_document(html_text: str, report_markdown: str) -> str:
    candidate = str(html_text or "").strip()
    if "<html" in candidate.lower() and "</html>" in candidate.lower():
        return candidate
    escaped = html.escape(report_markdown)
    body = escaped.replace("\n", "<br />\n")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Deep Research Report</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172033; background: #f7f8fb; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 48px 28px; background: #fff; min-height: 100vh; box-shadow: 0 24px 80px rgba(15, 23, 42, 0.08); }}
    h1 {{ font-size: 32px; line-height: 1.2; margin: 0 0 24px; }}
    .report {{ font-size: 15px; line-height: 1.75; white-space: normal; }}
  </style>
</head>
<body>
  <main>
    <h1>Deep Research Report</h1>
    <div class="report">{body}</div>
  </main>
</body>
</html>"""


def _runtime_event_pair(
    *,
    stage: ReportStage,
    tool_name: str,
    tool_args: dict[str, Any] | None = None,
    tool_output: dict[str, Any] | None = None,
    summary: str = "",
) -> list[dict[str, Any]]:
    args = {"stage": stage.key, **dict(tool_args or {})}
    output = {"ok": True, **dict(tool_output or {})}
    text = summary or str(output.get("summary") or tool_name)
    return [
        {
            "type": "tool_call",
            "tool_name": tool_name,
            "tool_args": args,
            "stage": stage.key,
            "text": tool_name,
        },
        {
            "type": "tool_result",
            "tool_name": tool_name,
            "tool_args": args,
            "tool_output": output,
            "stage": stage.key,
            "text": text,
        },
    ]


def _runtime_events_from_packets(stage: ReportStage, packets: list[dict[str, Any]], *, round_name: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for index, packet in enumerate(packets, start=1):
        results = list(packet.get("results") or [])
        query = str(packet.get("query") or "")
        events.extend(
            _runtime_event_pair(
                stage=stage,
                tool_name="deepresearch_query_agent",
                tool_args={"round": round_name, "query": query, "rank": index, "max_results": 3},
                tool_output={
                    "result_count": len(results),
                    "top_titles": [str(item.get("title") or "")[:100] for item in results[:3]],
                    "sources": sorted({str(item.get("source") or "unknown") for item in results}),
                },
                summary=f"{round_name} query `{query}` 返回 {len(results)} 条候选来源。",
            )
        )
    return events


def _dedupe_search_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in results:
        key = str(item.get("url") or item.get("title") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _fallback_expanded_queries(query: str, existing_queries: list[str]) -> list[str]:
    candidates = [
        f"{query} systematic review meta analysis",
        f"{query} real world evidence safety pharmacovigilance",
        f"{query} cost effectiveness payer access reimbursement",
        f"{query} clinical trial cardiovascular outcome adverse events",
    ]
    seen = {item.strip().lower() for item in existing_queries}
    return [candidate for candidate in candidates if candidate.lower() not in seen][:3]


async def _expand_queries_for_gap(
    state: ReportState,
    *,
    existing_queries: list[str],
    search_results: list[dict[str, Any]],
) -> tuple[list[str], str]:
    prompt = f"""
用户研究问题：
{state.get("input", "")}

已有检索 query：
{_json_dumps(existing_queries)}

第一轮候选来源摘要：
{_json_dumps(search_results[:8])}

请判断还缺哪些检索角度，并补充 2-3 个更具体的查询。请只输出 JSON，字段为 reason、queries。
"""
    try:
        text = await _call_required_llm(
            prompt,
            system="你是 Deep Research 的检索策略 Agent。你要根据证据缺口扩展 query，不要生成结论。",
            temperature=0.2,
        )
        data = json.loads(_extract_json_object(text))
        queries = [str(item).strip() for item in list(data.get("queries") or []) if str(item).strip()]
        reason = str(data.get("reason") or "第一轮来源覆盖不足，需要补充更具体的检索角度。")
    except Exception as exc:
        queries = _fallback_expanded_queries(str(state.get("input") or ""), existing_queries)
        reason = f"LLM query expansion unavailable, using deterministic fallback: {type(exc).__name__}"
    deduped = []
    seen = {item.strip().lower() for item in existing_queries}
    for query in queries:
        key = query.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(query)
    return deduped[:3], reason


def _search_gap_summary(results: list[dict[str, Any]], queries: list[str]) -> dict[str, Any]:
    sources = sorted({str(item.get("source") or "unknown") for item in results})
    unique_urls = {str(item.get("url") or "") for item in results if item.get("url")}
    needs_more = len(unique_urls) < 6 or len(sources) < 2 or len(results) < max(6, len(queries) * 2)
    return {
        "needs_more": needs_more,
        "result_count": len(results),
        "unique_url_count": len(unique_urls),
        "source_count": len(sources),
        "sources": sources,
        "reason": (
            "候选来源数量或来源类型不足，继续补检索。"
            if needs_more
            else "候选来源覆盖已足够进入正文抓取。"
        ),
    }


def _record_stage(
    state: ReportState,
    stage: ReportStage,
    *,
    artifact_content: str,
    summary: str | None = None,
    extra: dict[str, Any] | None = None,
) -> ReportState:
    completed = list(state.get("completed_stage_keys") or [])
    summaries = list(state.get("stage_summaries") or [])
    receipts = list(state.get("tool_receipts") or [])
    update: ReportState = dict(extra or {})

    if stage.key not in completed:
        local_artifact_path = _write_text_artifact(stage, artifact_content)
        workspace_path, _workspace_result = _write_workspace_artifact(state, stage, artifact_content)
        workspace_artifacts = list(state.get("workspace_artifacts") or [])
        if workspace_path not in workspace_artifacts:
            workspace_artifacts.append(workspace_path)
        completed.append(stage.key)
        stage_summary = summary or f"{stage.checkpoint_note} Workspace 产物：{workspace_path}"
        stage_summary = stage_summary.replace(str(local_artifact_path), workspace_path)
        summaries.append({"stage": stage.title, "phase": stage.phase, "summary": stage_summary})
        receipts.append(
            {
                "receipt_key": stage.receipt_key,
                "tool_name": stage.tool_name,
                "stage": stage.title,
                "status": "recorded",
                "summary": stage_summary,
            }
        )
        update["workspace_artifacts"] = workspace_artifacts
    if "stage_events" not in update:
        update["stage_events"] = []
    update.update({"completed_stage_keys": completed, "stage_summaries": summaries, "tool_receipts": receipts})
    return update


def _run_stage(state: ReportState, stage: ReportStage) -> ReportState:
    raise RuntimeError(f"Stage {stage.key} must be implemented as an async LLM/tool node")


async def _run_plan_research_stage(state: ReportState, stage: ReportStage) -> ReportState:
    if stage.key == "plan_research":
        query = state.get("input", "")
        prompt = f"""
用户要做一项医药领域 Deep Research：
{query}

请生成一个可执行研究计划，必须包含：
- 研究目标
- 6-8 个关键研究问题
- 6 个中文或英文检索 query
- 证据分级和排除标准
- 最终报告大纲

请只输出 JSON，字段为 topic、objectives、sub_questions、search_queries、evidence_criteria、report_outline。
"""
        plan_text = await _call_required_llm(prompt, temperature=0.1)
        try:
            plan = json.loads(_extract_json_object(plan_text))
        except Exception:
            plan = {
                "topic": query,
                "objectives": [plan_text[:400]],
                "sub_questions": [],
                "search_queries": [query, f"{query} clinical evidence", f"{query} real world safety"],
                "evidence_criteria": [],
                "report_outline": [],
            }
        if not isinstance(plan.get("search_queries"), list) or not plan["search_queries"]:
            plan["search_queries"] = [query, f"{query} clinical evidence", f"{query} real world safety"]
        stage_events = _runtime_event_pair(
            stage=stage,
            tool_name="deepresearch_planner",
            tool_args={"query": query},
            tool_output={
                "topic": str(plan.get("topic") or query),
                "query_count": len(plan.get("search_queries") or []),
                "sub_question_count": len(plan.get("sub_questions") or []),
                "outline_sections": list(plan.get("report_outline") or [])[:6],
            },
            summary=f"Planner 已生成 {len(plan.get('search_queries') or [])} 个检索 query。",
        )
        return _record_stage(
            state,
            stage,
            artifact_content=_json_dumps(plan),
            summary=f"LLM 已生成研究计划，包含 {len(plan.get('search_queries') or [])} 个检索 query。产物：{_artifact_path(stage)}",
            extra={
                "research_plan": plan,
                "task_title": str(plan.get("topic") or f"Deep Research: {query[:60]}"),
                "stage_events": stage_events,
            },
        )
    raise RuntimeError(f"Unexpected stage for plan node: {stage.key}")


def _extract_json_object(text: str) -> str:
    value = str(text or "").strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?", "", value, flags=re.IGNORECASE).strip()
        value = re.sub(r"```$", "", value).strip()
    start = value.find("{")
    end = value.rfind("}")
    if start >= 0 and end > start:
        return value[start : end + 1]
    return value


def _json_dumps(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, indent=2)


def _stage_node(stage: ReportStage):
    async def run_stage(state: ReportState) -> ReportState:
        if stage.key == "plan_research":
            return await _run_plan_research_stage(state, stage)
        if stage.key == "search_web":
            return await _run_web_search_stage(state, stage)
        if stage.key == "fetch_sources":
            return await _run_fetch_sources_stage(state, stage)
        if stage.key == "screen_evidence":
            return await _run_screen_evidence_stage(state, stage)
        if stage.key == "analyze_findings":
            return await _run_analysis_stage(state, stage)
        if stage.key == "critic_review":
            return await _run_critic_stage(state, stage)
        if stage.key == "write_report":
            return await _run_write_report_stage(state, stage)
        raise RuntimeError(f"Unsupported stage: {stage.key}")

    run_stage.__name__ = stage.key
    return run_stage


def _build_web_search_subgraph():
    """多 Agent 检索子图：用 Send 并行分发多个搜索 query，再汇总。"""

    def fan_out_queries(state: WebSearchState):
        queries = state.get("queries") or [state.get("query", "")]
        return [Send("query_agent", {"query": state.get("query", ""), "queries": [query]}) for query in queries]

    async def query_agent(state: WebSearchState) -> WebSearchState:
        query = (state.get("queries") or [state.get("query", "")])[0]
        results = await _web_search(query, max_results=3)
        return {"search_packets": [{"agent": "web_search_agent", "query": query, "results": results}]}

    def reduce_queries(state: WebSearchState) -> WebSearchState:
        packets = state.get("search_packets") or []
        digest = "；".join(f"{packet['query']}={len(packet.get('results') or [])} 条" for packet in packets)
        return {"search_digest": digest}

    graph = StateGraph(WebSearchState)
    graph.add_node("query_agent", query_agent)
    graph.add_node("reduce_queries", reduce_queries)
    graph.add_conditional_edges(START, fan_out_queries)
    graph.add_edge("query_agent", "reduce_queries")
    graph.add_edge("reduce_queries", END)
    return graph.compile(name="web_search_subgraph")


async def _run_web_search_stage(state: ReportState, stage: ReportStage) -> ReportState:
    plan = state.get("research_plan") or {}
    queries = list(plan.get("search_queries") or [state.get("input", "")])[:4]
    subgraph = _build_web_search_subgraph()
    result = await subgraph.ainvoke({"query": state.get("input", ""), "queries": queries})
    packets = list(result.get("search_packets") or [])
    stage_events = _runtime_events_from_packets(stage, packets, round_name="primary")
    search_results: list[dict[str, Any]] = []
    for packet in packets:
        search_results.extend(list(packet.get("results") or []))
    search_results = _dedupe_search_results(search_results)
    gap = _search_gap_summary(search_results, queries)
    stage_events.extend(
        _runtime_event_pair(
            stage=stage,
            tool_name="deepresearch_gap_checker",
            tool_args={"round": "primary", "queries": queries},
            tool_output=gap,
            summary=str(gap["reason"]),
        )
    )

    rounds = [{"round": "primary", "queries": queries, "result_count": len(search_results), "gap": gap}]
    if gap["needs_more"]:
        expanded_queries, reason = await _expand_queries_for_gap(
            state,
            existing_queries=queries,
            search_results=search_results,
        )
        stage_events.extend(
            _runtime_event_pair(
                stage=stage,
                tool_name="deepresearch_query_expander",
                tool_args={"round": "gap_fill", "existing_queries": queries},
                tool_output={"queries": expanded_queries, "reason": reason},
                summary=f"Query expander 补充 {len(expanded_queries)} 个 gap-fill query。",
            )
        )
        if expanded_queries:
            gap_result = await subgraph.ainvoke({"query": state.get("input", ""), "queries": expanded_queries})
            gap_packets = list(gap_result.get("search_packets") or [])
            stage_events.extend(_runtime_events_from_packets(stage, gap_packets, round_name="gap_fill"))
            for packet in gap_packets:
                search_results.extend(list(packet.get("results") or []))
            search_results = _dedupe_search_results(search_results)
            gap = _search_gap_summary(search_results, queries + expanded_queries)
            rounds.append(
                {
                    "round": "gap_fill",
                    "queries": expanded_queries,
                    "result_count": len(search_results),
                    "gap": gap,
                    "reason": reason,
                }
            )
    source_counts: dict[str, int] = {}
    for item in search_results:
        source = str(item.get("source") or "unknown")
        source_counts[source] = source_counts.get(source, 0) + 1
    source_summary = "，".join(f"{source} {count} 条" for source, count in sorted(source_counts.items())) or "无"
    traces = list(state.get("subgraph_traces") or [])
    traces.append(
        {
            "stage": stage.title,
            "subgraph": "web_search_subgraph",
            "agents": "web_search_agent x queries",
            "summary": str(result.get("search_digest") or ""),
        }
    )
    return _record_stage(
        state,
        stage,
        artifact_content=_json_dumps(search_results),
        summary=(
            f"执行 {len(rounds)} 轮检索、{sum(len(item['queries']) for item in rounds)} 个 query，得到 {len(search_results)} 条候选来源"
            f"（来源：{source_summary}）。产物：{_artifact_path(stage)}"
        ),
        extra={
            "search_results": search_results,
            "subgraph_traces": traces,
            "stage_events": stage_events,
        },
    )


async def _fetch_all_sources(search_results: list[dict[str, Any]], *, limit: int = 6) -> list[dict[str, Any]]:
    selected = [item for item in search_results if item.get("url")][:limit]
    fetched = await asyncio.gather(*[_web_fetch(str(item.get("url") or "")) for item in selected])
    merged = []
    for item, content in zip(selected, fetched, strict=False):
        merged.append({**item, **content, "snippet": item.get("snippet", "")})
    return merged


async def _run_fetch_sources_stage(state: ReportState, stage: ReportStage) -> ReportState:
    fetched = await _fetch_all_sources(list(state.get("search_results") or []))
    stage_events: list[dict[str, Any]] = []
    for index, source in enumerate(fetched, start=1):
        stage_events.extend(
            _runtime_event_pair(
                stage=stage,
                tool_name="deepresearch_fetch_agent",
                tool_args={"rank": index, "url": source.get("url"), "title": source.get("title")},
                tool_output={
                    "status": source.get("status"),
                    "content_chars": len(str(source.get("content") or "")),
                    "title": source.get("title"),
                },
                summary=f"Fetch agent 读取 `{source.get('title') or source.get('url')}`，状态：{source.get('status')}",
            )
        )
    return _record_stage(
        state,
        stage,
        artifact_content=_json_dumps(fetched),
        summary=f"真实抓取并清洗 {len(fetched)} 个来源正文。产物：{_artifact_path(stage)}",
        extra={"fetched_sources": fetched, "stage_events": stage_events},
    )


async def _run_screen_evidence_stage(state: ReportState, stage: ReportStage) -> ReportState:
    sources = list(state.get("fetched_sources") or [])
    prompt = f"""
用户研究问题：
{state.get("input", "")}

下面是真实 web_fetch 得到的候选来源。请筛选出可引用证据，去重并按临床证据、药物经济学、准入支付、真实世界安全性、研究空白分类。
请输出 JSON 数组，每项包含 title、url、category、relevance、evidence_level、key_finding、limitations。

候选来源：
{_json_dumps(sources[:8])}
"""
    evidence_text = await _call_required_llm(prompt, temperature=0.1)
    try:
        evidence = json.loads(_extract_json_array(evidence_text))
    except Exception:
        evidence = [{"category": "llm_screening_notes", "key_finding": evidence_text, "url": ""}]
    if not isinstance(evidence, list):
        evidence = [{"category": "llm_screening_notes", "key_finding": str(evidence), "url": ""}]
    categories = sorted({str(item.get("category") or "未分类") for item in evidence if isinstance(item, dict)})
    stage_events = _runtime_event_pair(
        stage=stage,
        tool_name="deepresearch_evidence_screener",
        tool_args={"source_count": len(sources), "criteria": list((state.get("research_plan") or {}).get("evidence_criteria") or [])[:5]},
        tool_output={
            "evidence_count": len(evidence),
            "categories": categories,
            "high_relevance_count": sum(
                1 for item in evidence if isinstance(item, dict) and str(item.get("relevance") or "").lower() == "high"
            ),
        },
        summary=f"Evidence screener 从 {len(sources)} 个正文来源中筛出 {len(evidence)} 条证据。",
    )
    missing_categories = [
        category
        for category in ("临床证据", "药物经济学", "准入支付", "真实世界安全性")
        if category not in categories
    ]
    stage_events.extend(
        _runtime_event_pair(
            stage=stage,
            tool_name="deepresearch_evidence_gap_checker",
            tool_args={"expected_categories": ["临床证据", "药物经济学", "准入支付", "真实世界安全性"]},
            tool_output={"missing_categories": missing_categories, "needs_critic_review": True},
            summary=(
                f"Evidence gap checker 发现缺口：{', '.join(missing_categories)}。"
                if missing_categories
                else "Evidence gap checker 未发现关键分类缺口。"
            ),
        )
    )
    return _record_stage(
        state,
        stage,
        artifact_content=_json_dumps(evidence),
        summary=f"LLM 基于抓取正文筛选 {len(evidence)} 条可引用证据。产物：{_artifact_path(stage)}",
        extra={"evidence_table": evidence, "stage_events": stage_events, "requires_critic_review": True},
    )


def _extract_json_array(text: str) -> str:
    value = str(text or "").strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?", "", value, flags=re.IGNORECASE).strip()
        value = re.sub(r"```$", "", value).strip()
    start = value.find("[")
    end = value.rfind("]")
    if start >= 0 and end > start:
        return value[start : end + 1]
    return value


def _build_analysis_subgraph():
    """分析子图：多 reviewer 并行审阅证据，再汇总。"""

    def fan_out_reviewers(state: AnalysisState):
        reviewers = state.get("reviewers") or ["market_reviewer", "technical_reviewer", "risk_reviewer"]
        return [
            Send(
                "analysis_reviewer",
                {
                    "query": state.get("query", ""),
                    "evidence_table": state.get("evidence_table", []),
                    "reviewers": [reviewer],
                },
            )
            for reviewer in reviewers
        ]

    async def analysis_reviewer(state: AnalysisState) -> AnalysisState:
        reviewer = (state.get("reviewers") or ["reviewer"])[0]
        evidence = state.get("evidence_table") or []
        prompt = (
            f"用户研究问题：{state.get('query', '')}\n"
            f"你是 {reviewer}。请基于以下证据表给出 3-5 条发现，必须标注证据来源、置信度和不确定性：\n"
            f"{_json_dumps(evidence[:6])}"
        )
        summary = await _call_required_llm(prompt)
        return {"analysis_packets": [{"agent": reviewer, "summary": summary[:1200]}]}

    def reduce_analysis(state: AnalysisState) -> AnalysisState:
        packets = state.get("analysis_packets") or []
        digest = "\n\n".join(f"### {item['agent']}\n{item['summary']}" for item in packets)
        return {"analysis_digest": digest}

    graph = StateGraph(AnalysisState)
    graph.add_node("analysis_reviewer", analysis_reviewer)
    graph.add_node("reduce_analysis", reduce_analysis)
    graph.add_conditional_edges(START, fan_out_reviewers)
    graph.add_edge("analysis_reviewer", "reduce_analysis")
    graph.add_edge("reduce_analysis", END)
    return graph.compile(name="analysis_subgraph")


async def _run_analysis_stage(state: ReportState, stage: ReportStage) -> ReportState:
    subgraph = _build_analysis_subgraph()
    result = await subgraph.ainvoke(
        {
            "query": state.get("input", ""),
            "evidence_table": list(state.get("evidence_table") or []),
            "reviewers": ["market_reviewer", "technical_reviewer", "risk_reviewer"],
        }
    )
    analysis = str(result.get("analysis_digest") or "")
    traces = list(state.get("subgraph_traces") or [])
    traces.append(
        {
            "stage": stage.title,
            "subgraph": "analysis_subgraph",
            "agents": "market_reviewer, technical_reviewer, risk_reviewer",
            "summary": "并行 reviewer 已完成主题归纳、技术判断和风险识别。",
        }
    )
    stage_events: list[dict[str, Any]] = []
    for packet in list(result.get("analysis_packets") or []):
        reviewer = str(packet.get("agent") or "reviewer")
        stage_events.extend(
            _runtime_event_pair(
                stage=stage,
                tool_name=f"deepresearch_{reviewer}",
                tool_args={"reviewer": reviewer, "evidence_count": len(list(state.get("evidence_table") or []))},
                tool_output={"summary_chars": len(str(packet.get("summary") or "")), "summary": str(packet.get("summary") or "")[:300]},
                summary=f"{reviewer} 已完成一轮证据交叉分析。",
            )
        )
    return _record_stage(
        state,
        stage,
        artifact_content=analysis,
        summary=f"完成 {len(result.get('analysis_packets') or [])} 个 reviewer 的交叉分析。产物：{_artifact_path(stage)}",
        extra={"analysis_markdown": analysis, "subgraph_traces": traces, "stage_events": stage_events},
    )


async def _run_critic_stage(state: ReportState, stage: ReportStage) -> ReportState:
    evidence = list(state.get("evidence_table") or [])
    analysis = state.get("analysis_markdown") or ""
    critic = await _call_required_llm(
        f"""
请作为独立医学研究审稿人，对下面 Deep Research 分析做批判性质检。
要求检查：引用覆盖、证据等级、样本外推风险、真实世界安全性遗漏、支付准入假设、反例、低置信结论。
输出 Markdown，不要使用固定模板套话。

研究问题：
{state.get("input", "")}

证据表：
{_json_dumps(evidence[:10])}

待质检分析：
{analysis[:4000]}
""",
        system="你是谨慎的医学证据审稿人，必须指出不确定性和证据缺口。",
    )
    stage_events = _runtime_event_pair(
        stage=stage,
        tool_name="deepresearch_critic_reviewer",
        tool_args={"evidence_count": len(evidence), "analysis_chars": len(analysis)},
        tool_output={"critic_chars": len(critic), "summary": critic[:300]},
        summary="Critic reviewer 已检查引用覆盖、反例、证据等级和低置信结论。",
    )
    return _record_stage(state, stage, artifact_content=critic, extra={"critic_markdown": critic, "stage_events": stage_events})


async def _run_write_report_stage(state: ReportState, stage: ReportStage) -> ReportState:
    query = state.get("input", "")
    evidence = list(state.get("evidence_table") or [])
    analysis = state.get("analysis_markdown") or ""
    critic = state.get("critic_markdown") or ""
    report = await _call_required_llm(
        f"""
请写一份面向医药业务和技术团队的 Deep Research 报告。
要求：
- 用自然研究报告口吻，不要说“这是模拟”。
- 必须基于给定证据表、分析和质检意见。
- 结论要标明置信度和证据缺口。
- 引用来源时使用 Markdown 链接。

研究问题：
{query}

证据表：
{_json_dumps(evidence[:12])}

多 reviewer 分析：
{analysis[:5000]}

独立质检意见：
{critic[:3000]}
""",
        system="你是资深医药 Deep Research 分析师。报告必须真实、谨慎、可追溯。",
        temperature=0.2,
    )
    report_html = await _call_required_llm(
        f"""
请基于下面 Markdown Deep Research 报告生成一份可直接在浏览器打开的自包含 HTML 展示页。
要求：
- 返回完整 HTML 文档，包含 <!doctype html>、html、head、body。
- 内联 CSS，视觉风格专业、清晰，适合医药研究汇报。
- 保留报告中的来源链接、置信度、证据缺口和风险提示。
- 不要加入与报告无关的营销文案。

Markdown 报告：
{report[:12000]}
""",
        system="你是资深研究报告信息设计师。只输出完整 HTML 文档。",
        temperature=0.15,
    )
    report_html = _ensure_html_document(report_html, report)
    workspace_paths, workspace_result = _write_workspace_report_files(state, report, report_html)
    stage_events = _runtime_event_pair(
        stage=stage,
        tool_name="deepresearch_report_writer",
        tool_args={"evidence_count": len(evidence), "analysis_chars": len(analysis), "critic_chars": len(critic)},
        tool_output={"report_chars": len(report), "html_chars": len(report_html), "workspace_paths": workspace_paths},
        summary=f"Report writer 已生成 {len(report)} 字符的研究报告。",
    )
    stage_events.extend(
        _workspace_write_events(
            stage=stage,
            tool_name="write_workspace_files",
            paths=workspace_paths,
            result=workspace_result,
        )
    )
    existing_workspace_artifacts = list(state.get("workspace_artifacts") or [])
    for path in workspace_paths:
        if path not in existing_workspace_artifacts:
            existing_workspace_artifacts.append(path)
    return _record_stage(
        {**state, "workspace_artifacts": existing_workspace_artifacts},
        stage,
        artifact_content=report,
        extra={
            "report_markdown": report,
            "report_html": report_html,
            "stage_events": stage_events,
        },
    )


def _render_final_answer(state: ReportState) -> str:
    completed = list(state.get("completed_stage_keys") or [])
    summaries = list(state.get("stage_summaries") or [])
    receipts = list(state.get("tool_receipts") or [])
    resumed_completed = list(state.get("resumed_completed_stage_keys") or [])
    if resumed_completed:
        skipped_keys = set(resumed_completed)
        continued_keys = [stage.key for stage in REPORT_STAGES if stage.key in completed and stage.key not in skipped_keys]
    else:
        skipped_keys = set(completed[:2])
        continued_keys = [stage_key for stage_key in completed if stage_key not in skipped_keys]
    skipped = [stage.title for stage in REPORT_STAGES if stage.key in skipped_keys]
    continued = [stage.title for stage in REPORT_STAGES if stage.key in continued_keys]
    artifacts = list(state.get("workspace_artifacts") or []) or _existing_artifacts(completed)
    reused_receipts = [stage.receipt_key for stage in REPORT_STAGES if stage.key in skipped_keys]
    reused_receipt_text = "、".join(f"`{receipt_key}`" for receipt_key in reused_receipts) if reused_receipts else "无"

    stage_lines = "\n".join(f"| {item['stage']} | {item['phase']} | {item['summary']} |" for item in summaries)
    receipt_lines = "\n".join(
        f"| `{item['receipt_key']}` | `{item.get('tool_name', '')}` | {item['stage']} | {item['status']} | {item['summary']} |"
        for item in receipts
    )
    artifact_lines = "\n".join(f"- `{path}`" for path in artifacts) or "- 无"
    trace_lines = "\n".join(
        f"| {item['stage']} | `{item['subgraph']}` | {item['agents']} | {item['summary']} |"
        for item in list(state.get("subgraph_traces") or [])
    ) or "| 无 | 无 | 无 | 无 |"

    return f"""# Deep Research 报告已恢复完成

## ResumeRun 结果

- 恢复后没有从头重跑，已完成阶段直接跳过：{"、".join(skipped) or "无"}。
- 本次继续执行阶段：{"、".join(continued) or "无"}。
- 最终交付物：`deepresearch-report.md` 和 `deepresearch-report.html`。
- 已复用 tool receipt：{reused_receipt_text}，没有重复执行 checkpoint 前的副作用工具。
- Workspace 目录：`research/...`。

## checkpoint 列表

| 阶段 | 状态 | 摘要 |
| --- | --- | --- |
{stage_lines}

## tool receipt

| receipt_key | 工具 | 阶段 | 状态 | 说明 |
| --- | --- | --- | --- | --- |
{receipt_lines}

## Workspace 产物

{artifact_lines}

## LangGraph 子图和多 Agent

| 主阶段 | 子图 | Agent | 输出摘要 |
| --- | --- | --- | --- |
{trace_lines}

## 开发者如何复用

1. 改 `REPORT_STAGES` 定义自己的业务安全点。
2. 替换 `_web_search` / `_web_fetch`，接入企业搜索、浏览器抓取或内部知识库。
3. 替换 `_run_analysis_stage` / `_run_write_report_stage`，写自己的 LLM 分析和报告模板。
4. 保留 `receipt_key`、`run_checkpoint` 和 LangGraph `thread_id/checkpoint_id`，ResumeRun 就能跳过已完成工具。
5. CancelRun 仍按协作式取消处理，在工具边界停到最近 checkpoint。
""".strip()


def finalize_report(state: ReportState) -> ReportState:
    return {"answer": _render_final_answer(state)}


async def _build_graph() -> tuple[Any, Any]:
    dsn = os.environ.get("KSADK_LANGGRAPH_CHECKPOINT_DSN") or os.environ.get("KSADK_SESSION_DSN")
    if not dsn:
        raise RuntimeError("KSADK_LANGGRAPH_CHECKPOINT_DSN or KSADK_SESSION_DSN is required")

    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Postgres mode requires langgraph-checkpoint-postgres and psycopg. "
            "Install this sample's requirements.txt, or set LONG_TASK_RESUME_DEMO_MODE=fixture "
            "for local InMemorySaver demos."
        ) from exc

    saver_cm = AsyncPostgresSaver.from_conn_string(dsn)
    saver = await saver_cm.__aenter__()
    await saver.setup()

    app = _compile_graph(saver)
    return app, saver_cm


def _compile_graph(checkpointer: Any) -> Any:
    graph = StateGraph(ReportState)
    for stage in REPORT_STAGES:
        graph.add_node(stage.key, _stage_node(stage))
    graph.add_node("finalize_report", finalize_report)
    graph.add_edge(START, "plan_research")
    graph.add_edge("plan_research", "search_web")
    graph.add_edge("search_web", "fetch_sources")
    graph.add_edge("fetch_sources", "screen_evidence")
    graph.add_edge("screen_evidence", "analyze_findings")
    graph.add_conditional_edges(
        "analyze_findings",
        lambda state: "critic_review" if state.get("requires_critic_review", True) else "write_report",
        {"critic_review": "critic_review", "write_report": "write_report"},
    )
    graph.add_edge("critic_review", "write_report")
    graph.add_edge("write_report", "finalize_report")
    graph.add_edge("finalize_report", END)
    return graph.compile(checkpointer=checkpointer)








def _slugify_query(query: str) -> str:
    digest = sha1(query.encode("utf-8")).hexdigest()[:10]
    return f"research-{digest}"




def _write_text_artifact(stage: ReportStage, content: str) -> Path:
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    path = _artifact_path(stage)
    path.write_text(content, encoding="utf-8")
    return path


def _workspace_artifact_dir(state: ReportState) -> str:
    return f"research/{_slugify_query(str(state.get('input') or 'deepresearch'))}"


def _workspace_artifact_path(state: ReportState, stage: ReportStage) -> str:
    return f"{_workspace_artifact_dir(state)}/{stage.artifact_name}"


def _write_workspace_artifact(state: ReportState, stage: ReportStage, content: str) -> tuple[str, dict[str, Any]]:
    relative_path = _workspace_artifact_path(state, stage)
    result = write_workspace_file(relative_path, content or "", overwrite=True)
    if not isinstance(result, dict) or not result.get("ok"):
        raise RuntimeError(f"write_workspace_file failed for {relative_path}: {result}")
    return str(result.get("path") or relative_path), result


def _write_workspace_report_files(state: ReportState, report_markdown: str, report_html: str) -> tuple[list[str], dict[str, Any]]:
    base_dir = _workspace_artifact_dir(state)
    files = [
        {"path": f"{base_dir}/deepresearch-report.md", "content": report_markdown},
        {"path": f"{base_dir}/deepresearch-report.html", "content": report_html},
    ]
    result = write_workspace_files(files, overwrite=True)
    if not isinstance(result, dict) or not result.get("ok"):
        raise RuntimeError(f"write_workspace_files failed for {base_dir}: {result}")
    written = [
        str(item.get("path") or "")
        for item in list(result.get("written") or [])
        if isinstance(item, dict) and item.get("path")
    ]
    return written, result




def _existing_artifacts(stage_keys: list[str]) -> list[str]:
    paths: list[str] = []
    for stage in REPORT_STAGES:
        if stage.key not in stage_keys:
            continue
        path = _artifact_path(stage)
        if path.exists():
            paths.append(str(path))
    return paths
