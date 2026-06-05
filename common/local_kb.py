from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CORPUS_DIR = Path(__file__).resolve().parent / "corpus"


@dataclass(frozen=True)
class LocalKnowledgeDocument:
    title: str
    source: str
    content: str


@dataclass(frozen=True)
class LocalKnowledgeResult:
    title: str
    source: str
    content: str
    score: float


def _tokenize(text: str) -> list[str]:
    normalized = str(text or "").lower()
    ascii_tokens = re.findall(r"[a-z0-9_+-]+", normalized)
    cjk_tokens = re.findall(r"[\u4e00-\u9fff]{2,}", normalized)
    return ascii_tokens + cjk_tokens


def load_documents(corpus_dir: Path | str = DEFAULT_CORPUS_DIR) -> list[LocalKnowledgeDocument]:
    root = Path(corpus_dir)
    documents: list[LocalKnowledgeDocument] = []
    for path in sorted(root.glob("*")):
        if path.suffix.lower() == ".md":
            content = path.read_text(encoding="utf-8")
            title = path.stem.replace("-", " ").replace("_", " ")
            first_heading = next(
                (line.lstrip("#").strip() for line in content.splitlines() if line.startswith("#")),
                "",
            )
            documents.append(
                LocalKnowledgeDocument(
                    title=first_heading or title,
                    source=path.name,
                    content=content.strip(),
                )
            )
        elif path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            items = payload if isinstance(payload, list) else payload.get("documents", [])
            for index, item in enumerate(items):
                documents.append(
                    LocalKnowledgeDocument(
                        title=str(item.get("title") or f"{path.stem}-{index + 1}"),
                        source=str(item.get("source") or path.name),
                        content=str(item.get("content") or "").strip(),
                    )
                )
    return [doc for doc in documents if doc.content]


def search_local_knowledge(
    query: str,
    *,
    top_k: int = 3,
    corpus_dir: Path | str = DEFAULT_CORPUS_DIR,
) -> list[LocalKnowledgeResult]:
    terms = set(_tokenize(query))
    if not terms:
        return []

    results: list[LocalKnowledgeResult] = []
    for doc in load_documents(corpus_dir):
        haystack = f"{doc.title}\n{doc.content}".lower()
        score = 0
        for term in terms:
            if term in haystack:
                score += haystack.count(term)
        if score:
            snippet = _snippet(doc.content, terms)
            results.append(
                LocalKnowledgeResult(
                    title=doc.title,
                    source=doc.source,
                    content=snippet,
                    score=float(score),
                )
            )
    results.sort(key=lambda item: (-item.score, item.source))
    return results[:top_k]


def format_local_knowledge_results(results: list[LocalKnowledgeResult]) -> str:
    if not results:
        return "未找到相关本地知识库内容。"
    parts: list[str] = []
    for index, result in enumerate(results, 1):
        parts.append(
            f"[{index}] (来源: {result.source}) {result.title}\n"
            f"{result.content}"
        )
    return "\n\n".join(parts)


def search_local_knowledge_text(query: str, *, top_k: int = 3) -> str:
    return format_local_knowledge_results(search_local_knowledge(query, top_k=top_k))


def _snippet(content: str, terms: set[str], *, max_chars: int = 360) -> str:
    compact = re.sub(r"\s+", " ", content).strip()
    lowered = compact.lower()
    first_hit = min((lowered.find(term) for term in terms if term in lowered), default=0)
    start = max(first_hit - 80, 0)
    end = min(start + max_chars, len(compact))
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(compact) else ""
    return f"{prefix}{compact[start:end]}{suffix}"

