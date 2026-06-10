from __future__ import annotations

from data import REPORT_OUTLINE, REPORT_SOURCES
from prompts import ROLE, SYSTEM_PROMPT, TITLE


def collect_report_sources(query: str) -> list[dict]:
    """收集报告引用材料。

    LangChain 运行时会把这个函数作为工具暴露给 root_agent；demo.py 也会直接调用它做离线演示。
    """

    text_query = query.lower()
    ranked = sorted(
        REPORT_SOURCES,
        key=lambda item: (sum(text_query.count(token) for token in item['title'].lower().split()), item['id']),
        reverse=True,
    )
    return ranked


def render_demo_answer(query: str) -> str:
    """生成离线报告，确保用户没有模型 key 也能看到完整效果。"""

    evidence = collect_report_sources(query)
    outline_lines = '\n'.join(f"{index}. {name}" for index, name in enumerate(REPORT_OUTLINE, 1))
    citation_lines = '\n'.join(
        f"- [{item['id']}] **{item['title']}**：{item['quote']}（章节：{item['section']}；来源：local-report-fixture）"
        for item in evidence
    )
    quality_lines = '\n'.join(f"- **{item['title']}**：{item['quality']}" for item in evidence)
    action_lines = '\n'.join(
        f"{index}. **{ROLE}撰写《{outline}》** - 基于材料《{evidence[(index - 1) % len(evidence)]['title']}》组织论证。"
        for index, outline in enumerate(REPORT_OUTLINE, 1)
    )
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith('这个场景')), '')
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 LangChain 版本使用 `create_agent` 和函数工具组织报告材料，适合对比 LangGraph 版本的显式工作流写法。

## 报告大纲

{outline_lines}

## 引用材料

{citation_lines}

## 质量检查

{quality_lines}

## 行动计划

{action_lines}

## 最终报告

LangChain 版本强调把报告材料检索做成可调用工具，Agent 可以在真实模型运行时主动调用 `collect_report_sources`，再基于引用材料输出报告。默认离线 demo 不访问外部搜索，避免伪造结果。

## 工程说明

- `agent.py` 暴露 LangChain `root_agent`。
- `tools.py` 同时服务 LangChain 工具调用和离线 demo。
- `data.py` 可替换为 Web Search、Knowledge Base 或 Workspace 文档。
""".strip()
