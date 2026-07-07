"""Web 检索/抓取层：ksadk 内置 web_search/web_fetch 优先 + 公开搜索/直抓 fallback。

从 agent.py 抽取的 web 工具层。test 通过 monkeypatch agent_module._web_search /
_fetch_with_ksadk_web_fetch / httpx.AsyncClient 控制；agent.py re-export 这些符号。
"""

from __future__ import annotations

import asyncio
import html
import json
import os
from hashlib import sha1
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import httpx

from ksadk.toolsets.web import web_fetch as _ksadk_web_fetch
from ksadk.toolsets.web import web_search as _ksadk_web_search

from stages import DEFAULT_SEARCH_PROVIDERS, SEARCH_USER_AGENT


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

