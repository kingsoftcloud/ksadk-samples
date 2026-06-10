from __future__ import annotations

from data import FEEDBACK_SIGNALS, KNOWLEDGE_ASSETS, RELEASE_CHECKS, UPDATE_PLAN
from prompts import SYSTEM_PROMPT, TITLE


def audit_knowledge_assets(query: str) -> list[dict]:
    """盘点现有知识资产。

    真实项目里这里可以替换为文档站、知识库、CMS 或搜索索引。
    """

    return KNOWLEDGE_ASSETS


def identify_knowledge_gaps(query: str) -> list[str]:
    """从用户反馈里识别知识缺口。"""

    return FEEDBACK_SIGNALS


def plan_knowledge_updates(query: str) -> list[dict]:
    """生成知识库更新计划。"""

    return UPDATE_PLAN


def _render_assets() -> str:
    lines = ["| 文档 ID | 标题 | 状态 | 用户信号 |", "| --- | --- | --- | --- |"]
    for item in KNOWLEDGE_ASSETS:
        lines.append(f"| `{item['id']}` | {item['title']} | {item['status']} | {item['signal']} |")
    return "\n".join(lines)


def _render_gaps() -> str:
    return "\n".join(f"- {item}" for item in FEEDBACK_SIGNALS)


def _render_updates() -> str:
    lines = ["| 目标 | 动作 | 负责人 |", "| --- | --- | --- |"]
    for item in UPDATE_PLAN:
        lines.append(f"| `{item['target']}` | {item['action']} | {item['owner']} |")
    return "\n".join(lines)


def _render_checks() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(RELEASE_CHECKS, 1))


def render_demo_answer(query: str) -> str:
    """生成离线知识运营更新计划。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实知识库、用户反馈和文档 CI。

## 知识盘点

{_render_assets()}

## 缺口分析

{_render_gaps()}

## 更新计划

{_render_updates()}

## 发布校验

{_render_checks()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责知识盘点、缺口识别、更新计划和发布校验。
- `data.py` 可替换为真实知识库、GitHub Issues、工单系统或文档 CI。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return audit_knowledge_assets(query) + [{"feedback": item} for item in identify_knowledge_gaps(query)]


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": item["owner"], "action": item["action"], "why": f"更新 {item['target']}。"}
        for index, item in enumerate(UPDATE_PLAN, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
