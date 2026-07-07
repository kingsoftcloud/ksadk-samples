"""长任务恢复示例的阶段定义、状态类型和常量。

从 agent.py 抽取的纯数据/类型层，零业务依赖，零循环 import 风险。
"""

from __future__ import annotations

import operator
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, TypedDict


@dataclass(frozen=True)
class ReportStage:
    key: str
    title: str
    phase: str
    receipt_key: str
    tool_name: str
    stream_line: str
    checkpoint_note: str
    next_action_detail: str
    artifact_name: str


REPORT_STAGES = (
    ReportStage(
        key="plan_research",
        title="规划研究问题",
        phase="已拆解研究目标、子问题、关键词和输出结构",
        receipt_key="deepresearch:plan:v1",
        tool_name="llm.plan",
        stream_line="1/7 规划研究问题：把用户问题拆成研究目标、关键子问题、检索关键词和报告结构。",
        checkpoint_note="研究计划已经固化，恢复后不需要重新澄清需求。",
        next_action_detail="继续检索公开网页",
        artifact_name="01-research-plan.json",
    ),
    ReportStage(
        key="search_web",
        title="检索公开网页",
        phase="已完成 web_search 候选来源检索",
        receipt_key="deepresearch:web_search:v1",
        tool_name="web.search",
        stream_line="2/7 检索公开网页：调用通用 web_search 工具获取候选来源、标题、链接和摘要。",
        checkpoint_note="候选来源已经记录，恢复后不会重复发起同一批搜索请求。",
        next_action_detail="继续抓取来源正文",
        artifact_name="02-search-results.json",
    ),
    ReportStage(
        key="fetch_sources",
        title="抓取来源正文",
        phase="已完成 web_fetch 正文抓取和清洗",
        receipt_key="deepresearch:web_fetch:v1",
        tool_name="web.fetch",
        stream_line="3/7 抓取来源正文：抓取候选来源正文，清洗标题、链接、正文片段和发布时间。",
        checkpoint_note="来源正文已经落入工作集，恢复后从证据筛选继续。",
        next_action_detail="继续筛选证据并去重",
        artifact_name="03-fetched-sources.json",
    ),
    ReportStage(
        key="screen_evidence",
        title="筛选证据并去重",
        phase="已完成相关性、可信度和重复度筛选",
        receipt_key="deepresearch:evidence_screen:v1",
        tool_name="evidence.screen",
        stream_line="4/7 筛选证据并去重：按相关性、可信度和重复度保留可引用材料。",
        checkpoint_note="可引用证据清单已经确定，恢复后直接进入交叉分析。",
        next_action_detail="继续交叉分析发现",
        artifact_name="04-evidence-table.json",
    ),
    ReportStage(
        key="analyze_findings",
        title="交叉分析发现",
        phase="已完成主题归纳、冲突识别和趋势判断",
        receipt_key="deepresearch:analysis:v1",
        tool_name="llm.analyze",
        stream_line="5/7 交叉分析发现：调用 LLM 对证据做主题归纳、冲突识别、趋势判断和缺口分析。",
        checkpoint_note="核心发现已经生成，可进入独立质检。",
        next_action_detail="继续批判性质检",
        artifact_name="05-analysis.md",
    ),
    ReportStage(
        key="critic_review",
        title="批判性质检",
        phase="已完成引用覆盖、反例和置信度检查",
        receipt_key="deepresearch:critic:v1",
        tool_name="llm.critic",
        stream_line="6/7 批判性质检：独立 reviewer 检查引用覆盖、推理跳跃、反例和置信度。",
        checkpoint_note="质检意见已经合并，恢复后只需要写最终报告。",
        next_action_detail="继续生成研究报告",
        artifact_name="06-critic-review.md",
    ),
    ReportStage(
        key="write_report",
        title="生成研究报告",
        phase="deep research 报告已生成并完成引用核查",
        receipt_key="deepresearch:report:v1",
        tool_name="workspace.write",
        stream_line="7/7 生成研究报告：写入摘要、证据表、主要发现、风险提示、参考链接和可复用模板。",
        checkpoint_note="最终报告和引用清单已写入工作区。",
        next_action_detail="任务已完成，无需再次恢复",
        artifact_name="deepresearch-report.md",
    ),
)


WORKSPACE_DIR = Path(os.environ.get("LONG_TASK_RESUME_WORKSPACE_DIR", ".agentengine/long-task-workspace"))


def _artifact_path(stage: "ReportStage") -> Path:
    return WORKSPACE_DIR / stage.artifact_name
RESEARCH_ACTION_KEYWORDS = (
    "调研",
    "研究",
    "分析",
    "比较",
    "整理",
    "生成",
    "写",
    "看看",
    "有哪些",
    "怎么选",
    "deepresearch",
    "deep research",
    "research",
)
EXPLICIT_BACKGROUND_KEYWORDS = ("长任务", "deepresearch", "deep research", "研究任务")
EXPLICIT_START_KEYWORDS = ("启动", "开始", "执行", "跑一个", "做一份", "生成", "创建")
GENERIC_RESEARCH_DOMAIN_HINTS = (
    "市场",
    "竞品",
    "行业",
    "产品",
    "技术",
    "公司",
    "政策",
    "趋势",
    "风险",
    "方案",
    "论文",
    "报告",
    "agent",
    "ai",
    "runtime",
)
DEFAULT_SEARCH_PROVIDERS = (
    ("bing", "https://cn.bing.com/search?q={query}&count={max_results}"),
    ("sogou", "https://www.sogou.com/web?query={query}"),
)
SEARCH_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36 "
    "KSADK-DeepResearch-Sample/1.0"
)


class ReportState(TypedDict, total=False):
    input: str
    task_title: str
    research_plan: dict[str, Any]
    search_results: list[dict[str, Any]]
    fetched_sources: list[dict[str, Any]]
    evidence_table: list[dict[str, Any]]
    analysis_markdown: str
    critic_markdown: str
    report_markdown: str
    completed_stage_keys: list[str]
    resumed_completed_stage_keys: list[str]
    stage_summaries: list[dict[str, str]]
    tool_receipts: list[dict[str, str]]
    stage_events: list[dict[str, Any]]
    subgraph_traces: list[dict[str, str]]
    workspace_artifacts: list[str]
    requires_critic_review: bool
    answer: str


class WebSearchState(TypedDict, total=False):
    query: str
    queries: list[str]
    search_packets: Annotated[list[dict[str, Any]], operator.add]
    search_digest: str


class AnalysisState(TypedDict, total=False):
    query: str
    evidence_table: list[dict[str, Any]]
    reviewers: list[str]
    analysis_packets: Annotated[list[dict[str, str]], operator.add]
    analysis_digest: str
