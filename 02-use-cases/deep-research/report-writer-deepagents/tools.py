from __future__ import annotations

from langchain_core.tools import tool

from data import REPORT_OUTLINE, REPORT_SOURCES
from prompts import ROLE, SYSTEM_PROMPT, TITLE


@tool
def collect_report_sources(query: str) -> list[dict]:
    """收集报告引用材料。"""

    return REPORT_SOURCES


def render_demo_answer(query: str) -> str:
    """生成离线报告，方便没有模型 key 时验证 DeepAgents 样例结构。"""

    evidence = REPORT_SOURCES
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

{goal_line} 当前 DeepAgents 版本把材料检索作为工具，适合扩展成长任务报告生成。

## 报告大纲

{outline_lines}

## 引用材料

{citation_lines}

## 质量检查

{quality_lines}

## 行动计划

{action_lines}

## 最终报告

DeepAgents 版本适合把报告生成拆成可复用工具和长任务上下文。默认离线 demo 只展示结构；接入真实模型后，Agent 可以调用 `collect_report_sources` 再生成更自然的报告。

## 工程说明

- `agent.py` 暴露 DeepAgents `root_agent`。
- `tools.py` 使用 `@tool` 包装材料检索。
- `data.py` 可替换为搜索、知识库或 Workspace 文档。
""".strip()
