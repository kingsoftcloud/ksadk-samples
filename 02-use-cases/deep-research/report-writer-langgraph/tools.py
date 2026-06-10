from __future__ import annotations

from data import REPORT_OUTLINE, REPORT_SOURCES
from prompts import ROLE, SYSTEM_PROMPT, TITLE


def _score(query: str, item: dict) -> int:
    """按问题关键词选择报告材料。

    这里用透明规则代替真实搜索，保证开源样例离线可运行。
    接入真实 Web Search 或 KSADK Knowledge Base 时，可以把这个函数替换成搜索工具调用。
    """

    text = f"{item['title']} {item['quote']} {item['section']}".lower()
    tokens = [part for part in query.lower().replace('，', ' ').replace('。', ' ').split() if part]
    return sum(text.count(token) for token in tokens) or int(any(ch in text for ch in query[:10]))


def collect_evidence(query: str) -> list[dict]:
    """收集报告引用材料。"""

    ranked = sorted(REPORT_SOURCES, key=lambda item: (_score(query, item), item['id']), reverse=True)
    return [
        {
            'id': item['id'],
            'title': item['title'],
            'summary': item['quote'],
            'section': item['section'],
            'quality': item['quality'],
            'source': 'local-report-fixture',
        }
        for item in ranked[:4]
    ]


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """把引用材料组织成报告写作步骤。"""

    actions = []
    for index, outline in enumerate(REPORT_OUTLINE, 1):
        evidence_title = evidence[(index - 1) % len(evidence)]['title'] if evidence else '本地材料'
        actions.append(
            {
                'step': index,
                'owner': ROLE,
                'action': f'撰写《{outline}》',
                'why': f"基于材料《{evidence_title}》组织论证。",
            }
        )
    return actions


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """渲染一份适合 Web UI 展示的研究报告草稿。"""

    outline_lines = '\n'.join(f"{index}. {name}" for index, name in enumerate(REPORT_OUTLINE, 1))
    citation_lines = '\n'.join(
        f"- [{item['id']}] **{item['title']}**：{item['summary']}（章节：{item['section']}；来源：{item['source']}）"
        for item in evidence
    ) or '- 暂无引用材料。'
    quality_lines = '\n'.join(
        f"- **{item['title']}**：{item['quality']}"
        for item in evidence
    ) or '- 需要补充引用材料后再检查质量。'
    action_lines = '\n'.join(
        f"{item['step']}. **{item['action']}** - {item['why']}"
        for item in actions
    ) or '1. 补充材料后重新生成报告。'
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith('这个场景')), '')
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line or '这个 demo 已生成一份可复现报告。'} 当前报告使用本地公开材料生成，适合替换为 Web Search、Knowledge Base 或 Workspace 文档后继续扩展。

## 报告大纲

{outline_lines}

## 引用材料

{citation_lines}

## 质量检查

{quality_lines}

## 行动计划

{action_lines}

## 最终报告

### 摘要

企业 Agent Runtime Platform 的选型不应只比较框架 API，还要看本地调试、浏览器调试、工具边界、可观测性和部署链路是否统一。

### 关键发现

- 统一运行时能降低从 demo 到部署的迁移成本。
- Workspace、Sandbox、Skill Runtime 的边界越清晰，越容易把高风险能力交给平台治理。
- Web UI、trace 和可运行样例会显著影响开发者是否愿意继续试用。

### 风险和限制

- 当前样例未调用真实搜索或云端知识库，所有引用都来自本地 fixture。
- 上线前仍需要补充真实 trace、权限策略和部署环境验证。

### 落地建议

先用本样例跑通报告结构，再把 `collect_evidence` 替换为 Knowledge Base 或 Web Search，把 `quality` 字段替换为真实评审规则。

## 工程说明

- `agent.py` 只负责暴露 KSADK 入口。
- `workflow.py` 负责 LangGraph 编排。
- `tools.py` 负责报告材料检索、质量检查和 Markdown 报告渲染。
- `data.py` 和 `prompts.py` 存放可替换的材料和写作约束。
""".strip()


def render_demo_answer(query: str) -> str:
    """供 demo.py、测试和其他框架版本复用的离线报告生成入口。"""

    evidence = collect_evidence(query)
    actions = plan_actions(query, evidence)
    return render_answer(query, evidence, actions)
