from __future__ import annotations

from data import APPROVAL_RISKS, NEGOTIATION_ITEMS, PROCUREMENT_REQUESTS, VENDORS
from prompts import SYSTEM_PROMPT, TITLE


def load_procurement_requests(query: str) -> list[dict]:
    """读取采购需求。

    真实项目里这里可以替换为采购申请、预算、验收标准和审批流。
    """

    return PROCUREMENT_REQUESTS


def compare_vendors(query: str) -> list[dict]:
    """对比供应商。"""

    return sorted(VENDORS, key=lambda item: item["score"], reverse=True)


def plan_negotiation(query: str) -> list[str]:
    """生成谈判计划。"""

    return NEGOTIATION_ITEMS


def _render_requests() -> str:
    lines = ["| 采购项 | 数量 | 优先级 | 要求 |", "| --- | --- | --- | --- |"]
    for item in PROCUREMENT_REQUESTS:
        lines.append(f"| {item['item']} | {item['quantity']} | {item['priority']} | {item['requirement']} |")
    return "\n".join(lines)


def _render_vendors() -> str:
    lines = ["| 供应商 | 评分 | 优势 | 风险 |", "| --- | ---: | --- | --- |"]
    for item in compare_vendors(""):
        lines.append(f"| {item['name']} | {item['score']} | {item['strength']} | {item['risk']} |")
    return "\n".join(lines)


def _render_negotiation() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(NEGOTIATION_ITEMS, 1))


def _render_approval_risks() -> str:
    lines = ["| 风险 | 责任方 | 缓解动作 |", "| --- | --- | --- |"]
    for item in APPROVAL_RISKS:
        lines.append(f"| {item['risk']} | {item['owner']} | {item['mitigation']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线采购协同方案。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实采购申请、供应商库和审批流。

## 采购需求

{_render_requests()}

## 供应商对比

{_render_vendors()}

## 谈判计划

{_render_negotiation()}

## 审批风险

{_render_approval_risks()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责采购需求、供应商对比、谈判计划和审批风险。
- `data.py` 可替换为真实采购系统、供应商库、审批流或合同管理系统。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return load_procurement_requests(query) + compare_vendors(query) + APPROVAL_RISKS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "采购协同负责人", "action": item, "why": "推进供应商筛选和谈判。"}
        for index, item in enumerate(NEGOTIATION_ITEMS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
