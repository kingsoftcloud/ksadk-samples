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


async def _call_chat_model(messages: list[dict[str, str]], *, temperature: float = 0.2) -> str:
    if not _model_configured():
        return ""
    base_url = os.environ["OPENAI_BASE_URL"].rstrip("/")
    api_key = os.environ["OPENAI_API_KEY"]
    model = os.environ["OPENAI_MODEL_NAME"]
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": messages, "stream": False, "temperature": temperature},
        )
        response.raise_for_status()
        data = response.json()
    choices = data.get("choices") if isinstance(data, dict) else None
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if content:
            return str(content)
    return ""


async def _stream_chat_model(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.2,
) -> AsyncIterator[str]:
    if not _model_configured():
        raise RuntimeError(
            "模型未配置：真实 Deep Research demo 需要 OPENAI_API_KEY、OPENAI_BASE_URL、OPENAI_MODEL_NAME。"
        )
    base_url = os.environ["OPENAI_BASE_URL"].rstrip("/")
    api_key = os.environ["OPENAI_API_KEY"]
    model = os.environ["OPENAI_MODEL_NAME"]
    async with httpx.AsyncClient(timeout=90) as client:
        async with client.stream(
            "POST",
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": messages, "stream": True, "temperature": temperature},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                payload = line.removeprefix("data:").strip()
                if not payload or payload == "[DONE]":
                    continue
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                choices = data.get("choices") if isinstance(data, dict) else None
                if not isinstance(choices, list) or not choices:
                    continue
                choice = choices[0] if isinstance(choices[0], dict) else {}
                delta = choice.get("delta") if isinstance(choice, dict) else {}
                content = delta.get("content") if isinstance(delta, dict) else None
                if content:
                    yield str(content)


async def _call_required_llm(
    prompt: str,
    *,
    system: str = "你是严谨的 Deep Research 研究员。必须基于输入资料生成内容，不要编造来源。",
    temperature: float = 0.2,
) -> str:
    content = await _call_chat_model(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    if not content.strip():
        raise RuntimeError("LLM 没有返回可用内容")
    return content.strip()


_KSADK_SEARCH_CACHE: dict[str, list[dict[str, Any]]] = {}


def _ksadk_web_search_configured() -> bool:
    """ksadk 内置 web_search 是否启用（KSADK_WEB_SEARCH_PROVIDER=ksyun）。"""
    return os.environ.get("KSADK_WEB_SEARCH_PROVIDER", "").strip().lower() == "ksyun"


async def _search_with_ksadk_web_search(query: str, *, max_results: int = 5) -> list[dict[str, Any]]:
    """优先走 ksadk 内置 web_search（ksyun provider，复用 KSADK_MCP_KEY）。未配置或失败返回 [] 触发降级。"""
    cache_key = f"ksyun::{query}::{max_results}"
    cached = _KSADK_SEARCH_CACHE.get(cache_key)
    if cached is not None:
        return cached
    if not _ksadk_web_search_configured():
        return []
    try:
        result = await asyncio.to_thread(_ksadk_web_search, query, max_results)
    except Exception:
        return []
    if not isinstance(result, dict) or not result.get("ok"):
        return []
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in result.get("results") or []:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or item.get("link") or "")
        if not url or url in seen:
            continue
        seen.add(url)
        normalized.append(
            {
                "title": str(item.get("title") or "未命名来源"),
                "url": url,
                "snippet": str(item.get("snippet") or item.get("summary") or ""),
                "query": query,
                "source": "ksyun:web_search",
                "published_at": str(item.get("date") or ""),
            }
        )
        if len(normalized) >= max_results:
            break
    if normalized:
        _KSADK_SEARCH_CACHE[cache_key] = normalized
    return normalized


async def _web_search(query: str, *, max_results: int = 5) -> list[dict[str, Any]]:
    ksadk_results = await _search_with_ksadk_web_search(query, max_results=max_results)
    if ksadk_results:
        return ksadk_results
    endpoint = os.environ.get("DEEPRESEARCH_WEB_SEARCH_URL", "").strip()
    if endpoint:
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(
                    endpoint,
                    params={"q": query, "max_results": max_results},
                    headers={"User-Agent": SEARCH_USER_AGENT},
                )
                response.raise_for_status()
                data = response.json()
            items = data.get("results") if isinstance(data, dict) else data
            if isinstance(items, list):
                normalized = []
                for item in items[:max_results]:
                    if not isinstance(item, dict):
                        continue
                    normalized.append(
                        {
                            "title": str(item.get("title") or item.get("name") or "未命名来源"),
                            "url": str(item.get("url") or item.get("link") or ""),
                            "snippet": str(item.get("snippet") or item.get("summary") or ""),
                            "query": query,
                            "source": "configured_api",
                        }
                    )
                if normalized:
                    return normalized
        except Exception as exc:
            configured_error = f"{type(exc).__name__}: {exc}"
        else:
            configured_error = "configured search returned no usable results"
    else:
        configured_error = ""
    live_results = await _search_public_web(query, max_results=max_results)
    if live_results:
        return live_results
    fallback = _fallback_search_results(query, max_results=max_results)
    if configured_error:
        for item in fallback:
            item["snippet"] = f"{item['snippet']} 配置搜索失败：{configured_error}"
    return fallback


async def _search_public_web(query: str, *, max_results: int = 5) -> list[dict[str, Any]]:
    providers = _configured_search_providers()
    headers = {"User-Agent": SEARCH_USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6"}
    async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers=headers) as client:
        for source, template in providers:
            try:
                url = template.format(query=quote_plus(query), max_results=max_results)
                response = await client.get(url)
                response.raise_for_status()
                results = _parse_search_html(response.text, query=query, source=source, max_results=max_results)
                if results:
                    return results
            except Exception:
                continue
    return []


def _configured_search_providers() -> list[tuple[str, str]]:
    raw = os.environ.get("DEEPRESEARCH_SEARCH_PROVIDERS", "").strip()
    if not raw:
        return list(DEFAULT_SEARCH_PROVIDERS)
    providers: list[tuple[str, str]] = []
    for item in raw.split(","):
        name = item.strip().lower()
        if not name:
            continue
        for provider_name, template in DEFAULT_SEARCH_PROVIDERS:
            if provider_name == name:
                providers.append((provider_name, template))
                break
    return providers or list(DEFAULT_SEARCH_PROVIDERS)


def _parse_search_html(html_text: str, *, query: str, source: str, max_results: int = 5) -> list[dict[str, Any]]:
    parser = _SearchResultParser(source=source)
    parser.feed(html_text)
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in parser.results:
        url = _normalize_search_url(item.get("url", ""))
        title = _compact_text(item.get("title", ""))
        snippet = _compact_text(item.get("snippet", ""))
        if not url or not title or url in seen or _is_noise_url(url):
            continue
        seen.add(url)
        results.append({"title": title, "url": url, "snippet": snippet, "query": query, "source": source})
        if len(results) >= max_results:
            break
    return results


class _SearchResultParser(HTMLParser):
    def __init__(self, *, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.results: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None
        self._capture: str | None = None
        self._capture_parts: list[str] = []
        self._container_text: list[str] = []
        self._tag_stack: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        class_name = attr.get("class", "")
        self._tag_stack.append((tag, attr))
        if tag in {"li", "div"} and self._looks_like_result_container(class_name):
            self._flush_current()
            self._current = {}
            self._container_text = []
        if tag == "a" and self._current is not None and not self._current.get("url"):
            href = attr.get("href", "")
            if href:
                self._current["url"] = href
                self._capture = "title"
                self._capture_parts = []
        elif tag == "p" and self._current is not None:
            self._capture = "snippet"
            self._capture_parts = []

    def handle_endtag(self, tag: str) -> None:
        if self._capture == "title" and tag == "a" and self._current is not None:
            self._current["title"] = _compact_text(" ".join(self._capture_parts))
            self._capture = None
            self._capture_parts = []
        elif self._capture == "snippet" and tag == "p" and self._current is not None:
            self._current["snippet"] = _compact_text(" ".join(self._capture_parts))
            self._capture = None
            self._capture_parts = []
        if tag in {"li", "div"} and self._current is not None:
            self._flush_current()
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._container_text.append(data)
        if self._capture:
            self._capture_parts.append(data)

    def close(self) -> None:
        self._flush_current()
        super().close()

    def _looks_like_result_container(self, class_name: str) -> bool:
        if self.source == "bing":
            return "b_algo" in class_name
        if self.source == "sogou":
            return any(token in class_name for token in ("vrwrap", "rb", "results"))
        return any(token in class_name for token in ("result", "b_algo", "vrwrap"))

    def _flush_current(self) -> None:
        if self._current and self._current.get("url") and self._current.get("title"):
            if not self._current.get("snippet"):
                title = _compact_text(self._current.get("title", ""))
                text = _compact_text(" ".join(self._container_text))
                if title and text.startswith(title):
                    text = text[len(title) :].strip()
                self._current["snippet"] = text[:300]
            self.results.append(dict(self._current))
        self._current = None
        self._capture = None
        self._capture_parts = []
        self._container_text = []


class _ReadableTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.parts: list[str] = []
        self._skip_depth = 0
        self._in_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"script", "style", "noscript", "svg", "canvas"}:
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
            self._title_parts = []
        elif tag in {"p", "br", "li", "div", "section", "article", "h1", "h2", "h3"} and not self._skip_depth:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg", "canvas"} and self._skip_depth:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False
            self.title = _compact_text(" ".join(self._title_parts))[:160]

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self._title_parts.append(data)
        else:
            self.parts.append(data)

    @property
    def text(self) -> str:
        return _compact_text(" ".join(self.parts))


def _compact_text(value: str) -> str:
    return " ".join(html.unescape(str(value or "")).split())


def _normalize_search_url(url: str) -> str:
    value = html.unescape(str(url or "").strip())
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.path in {"/link", "/ck/a"}:
        params = parse_qs(parsed.query)
        for key in ("url", "u"):
            candidate = params.get(key, [""])[0]
            if candidate:
                return unquote(candidate)
    if value.startswith("//"):
        return "https:" + value
    return value


def _is_noise_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if not parsed.scheme.startswith("http"):
        return True
    return any(token in host for token in ("bing.com", "sogou.com", "baidu.com")) and (
        "/search" in parsed.path or "cache" in parsed.path
    )



def _fallback_search_results(query: str, *, max_results: int = 5) -> list[dict[str, Any]]:
    slug = sha1(query.encode("utf-8")).hexdigest()[:8]
    templates = [
        ("官方文档", "https://example.com/official-docs"),
        ("行业报告", "https://example.com/industry-report"),
        ("竞品分析", "https://example.com/competitive-analysis"),
        ("案例复盘", "https://example.com/case-study"),
        ("风险讨论", "https://example.com/risk-review"),
    ]
    return [
        {
            "title": f"{name}：{query[:48]}",
            "url": f"{url}/{slug}-{index}",
            "snippet": f"围绕「{query}」的{name}摘要。真实搜索不可用时使用此降级结果，生产环境应接入 DEEPRESEARCH_WEB_SEARCH_URL。",
            "query": query,
            "source": "fallback",
        }
        for index, (name, url) in enumerate(templates[:max_results], start=1)
    ]


async def _fetch_with_ksadk_web_fetch(url: str) -> dict[str, Any] | None:
    """用 ksadk 内置 web_fetch（含 SSRF 防护 + HTML 清洗 + 结果预算）。失败返回 None 触发降级。"""
    if not url:
        return None
    try:
        result = await asyncio.to_thread(_ksadk_web_fetch, url, 4000)
    except Exception:
        return None
    if not isinstance(result, dict) or not result.get("ok"):
        return None
    text = str(result.get("text") or "")
    if not text:
        return None
    return {
        "url": url,
        "title": url,
        "content": text[:4000],
        "status": "fetched",
        "source": "ksadk:web_fetch",
    }


async def _web_fetch(url: str) -> dict[str, Any]:
    if not url:
        return {"url": url, "title": "空 URL", "content": "未提供 URL。", "status": "missing_url"}
    ksadk_result = await _fetch_with_ksadk_web_fetch(url)
    if ksadk_result is not None:
        return ksadk_result
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "KSADK-DeepResearch-Sample/1.0"})
            response.raise_for_status()
            text = response.text
        parser = _ReadableTextParser()
        parser.feed(text)
        cleaned = parser.text[:4000]
        title = parser.title or _extract_html_title(text) or url
        return {"url": url, "title": title, "content": cleaned, "status": "fetched"}
    except Exception as exc:
        return {
            "url": url,
            "title": url,
            "content": f"网页抓取降级：{type(exc).__name__}: {exc}",
            "status": "fallback",
        }


def _extract_html_title(text: str) -> str:
    lowered = text.lower()
    start = lowered.find("<title")
    if start < 0:
        return ""
    start = lowered.find(">", start)
    end = lowered.find("</title>", start)
    if start < 0 or end < 0:
        return ""
    return " ".join(text[start + 1 : end].split())[:160]


def _slugify_query(query: str) -> str:
    digest = sha1(query.encode("utf-8")).hexdigest()[:10]
    return f"research-{digest}"


def _artifact_path(stage: ReportStage) -> Path:
    return WORKSPACE_DIR / stage.artifact_name


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


def _model_configured() -> bool:
    return bool(
        os.environ.get("OPENAI_API_KEY")
        and os.environ.get("OPENAI_BASE_URL")
        and os.environ.get("OPENAI_MODEL_NAME")
    )


def _existing_artifacts(stage_keys: list[str]) -> list[str]:
    paths: list[str] = []
    for stage in REPORT_STAGES:
        if stage.key not in stage_keys:
            continue
        path = _artifact_path(stage)
        if path.exists():
            paths.append(str(path))
    return paths


def _stage_by_key(stage_key: str) -> ReportStage:
    for stage in REPORT_STAGES:
        if stage.key == stage_key:
            return stage
    return REPORT_STAGES[0]


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
