from __future__ import annotations

from data import DATA_ASSETS, GOVERNANCE_ACTIONS, QUALITY_ISSUES, RESPONSIBILITY_MATRIX
from prompts import SYSTEM_PROMPT, TITLE


def load_data_assets(query: str) -> list[dict]:
    """读取数据资产清单。

    真实项目里这里可以替换为数据目录、表元数据、血缘和使用方。
    """

    return DATA_ASSETS


def audit_quality_issues(query: str) -> list[dict]:
    """审计数据质量问题。"""

    severity_rank = {"高": 0, "中": 1, "低": 2}
    return sorted(QUALITY_ISSUES, key=lambda item: severity_rank.get(item["severity"], 9))


def plan_governance_actions(query: str) -> list[str]:
    """生成治理计划。"""

    return GOVERNANCE_ACTIONS


def _render_assets() -> str:
    lines = ["| 资产 | Owner | 用途 | 使用方 |", "| --- | --- | --- | --- |"]
    for item in DATA_ASSETS:
        lines.append(f"| {item['asset']} | {item['owner']} | {item['usage']} | {item['consumer']} |")
    return "\n".join(lines)


def _render_issues() -> str:
    lines = ["| 问题 | 严重度 | 资产 | 整改动作 |", "| --- | --- | --- | --- |"]
    for item in audit_quality_issues(""):
        lines.append(f"| {item['issue']} | {item['severity']} | {item['asset']} | {item['action']} |")
    return "\n".join(lines)


def _render_plan() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(GOVERNANCE_ACTIONS, 1))


def _render_matrix() -> str:
    lines = ["| 责任方 | 范围 | 交付物 |", "| --- | --- | --- |"]
    for item in RESPONSIBILITY_MATRIX:
        lines.append(f"| {item['owner']} | {item['scope']} | {item['deliverable']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线数据治理审计报告。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实数据目录、质量规则、调度日志和整改工单。

## 资产清单

{_render_assets()}

## 质量问题

{_render_issues()}

## 治理计划

{_render_plan()}

## 责任矩阵

{_render_matrix()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责资产清单、质量问题、治理计划和责任矩阵。
- `data.py` 可替换为真实数据目录、质量规则、调度日志、血缘或工单系统。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return load_data_assets(query) + audit_quality_issues(query) + RESPONSIBILITY_MATRIX


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "数据治理负责人", "action": item, "why": "让质量问题可追踪、可验收。"}
        for index, item in enumerate(GOVERNANCE_ACTIONS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
