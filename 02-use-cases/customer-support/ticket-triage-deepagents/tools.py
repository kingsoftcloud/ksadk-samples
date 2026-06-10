from __future__ import annotations

from langchain_core.tools import tool

from data import ESCALATION_POLICY, KNOWLEDGE_ARTICLES, REPLY_STEPS
from prompts import SYSTEM_PROMPT, TITLE


@tool
def search_support_knowledge(query: str) -> list[dict]:
    """检索客服知识。

    默认使用本地 fixture；真实项目可以替换为 KSADK Knowledge Base 或工单系统搜索接口。
    """

    return _search_support_knowledge(query)


@tool
def classify_ticket(query: str) -> dict:
    """根据问题现象生成工单摘要。"""

    articles = _search_support_knowledge(query)
    primary = articles[0]
    return {
        "title": primary["title"],
        "severity": primary["severity"],
        "impact": "影响本地调试或客户验证路径，需要优先确认运行时和工具链状态。",
        "matched_article": primary["id"],
    }


def _search_support_knowledge(query: str) -> list[dict]:
    normalized = query.lower()
    ranked = sorted(
        KNOWLEDGE_ARTICLES,
        key=lambda item: sum(str(value).lower().count(token) for value in item.values() for token in normalized.split()),
        reverse=True,
    )
    return ranked[:3]


def _classify_ticket(query: str) -> dict:
    articles = _search_support_knowledge(query)
    primary = articles[0]
    return {
        "title": primary["title"],
        "severity": primary["severity"],
        "impact": "影响本地调试或客户验证路径，需要优先确认运行时和工具链状态。",
        "matched_article": primary["id"],
    }


def _render_knowledge(articles: list[dict]) -> str:
    lines = []
    for item in articles:
        lines.append(
            f"- **{item['title']}**（{item['id']}，{item['severity']}）：{item['symptom']} 处理建议：{item['resolution']}"
        )
    return "\n".join(lines)


def _render_escalation(severity: str) -> str:
    policy = next((item for item in ESCALATION_POLICY if item["level"] == severity), ESCALATION_POLICY[-1])
    lines = [
        f"- 当前建议等级：**{policy['level']}**。",
        f"- 触发条件：{policy['condition']}。",
        f"- 升级对象：{policy['target']}。",
    ]
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线客服工单处理建议。"""

    ticket = _classify_ticket(query)
    articles = _search_support_knowledge(query)
    step_lines = "\n".join(f"{index}. {step}" for index, step in enumerate(REPLY_STEPS, 1))
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地客服知识 fixture，不伪造真实工单系统结果；接入 Knowledge Base 或工单 API 后可复用同一套分级流程。

## 工单摘要

- 标题：{ticket['title']}
- 严重等级：{ticket['severity']}
- 影响判断：{ticket['impact']}
- 命中知识：`{ticket['matched_article']}`

## 知识匹配

{_render_knowledge(articles)}

## 处理步骤

{step_lines}

## 升级策略

{_render_escalation(ticket['severity'])}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责知识匹配、工单分级和升级策略。
- `data.py` 可替换为真实知识库、工单系统或客服 API。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return _search_support_knowledge(query)


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "客户支持专家", "action": step, "why": "保证客户回复可执行、可升级、可追踪。"}
        for index, step in enumerate(REPLY_STEPS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
