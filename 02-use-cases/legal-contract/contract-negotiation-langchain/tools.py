from __future__ import annotations

from data import CONTRACT_SUMMARY, KEY_CLAUSES, LEGAL_RISKS, NEGOTIATION_POINTS
from prompts import SYSTEM_PROMPT, TITLE


def load_contract_summary(query: str) -> dict:
    """读取合同摘要。

    真实项目里这里可以替换为合同管理系统、法务规则库、审批流和历史谈判记录。
    """

    return CONTRACT_SUMMARY


def extract_key_clauses(query: str) -> list[dict]:
    """提取关键条款。"""

    return KEY_CLAUSES


def draft_negotiation_points(query: str) -> list[str]:
    """生成谈判建议。"""

    return NEGOTIATION_POINTS


def _render_summary() -> str:
    return (
        f"- 合同：{CONTRACT_SUMMARY['name']}\n"
        f"- 相对方：{CONTRACT_SUMMARY['counterparty']}\n"
        f"- 金额：{CONTRACT_SUMMARY['amount']}\n"
        f"- 周期：{CONTRACT_SUMMARY['term']}\n"
        f"- 目的：{CONTRACT_SUMMARY['purpose']}"
    )


def _render_clauses() -> str:
    lines = ["| 条款 | 状态 | 审阅要点 |", "| --- | --- | --- |"]
    for item in extract_key_clauses(""):
        lines.append(f"| {item['clause']} | {item['status']} | {item['note']} |")
    return "\n".join(lines)


def _render_negotiation() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(NEGOTIATION_POINTS, 1))


def _render_risks() -> str:
    lines = ["| 风险 | 级别 | 缓解动作 |", "| --- | --- | --- |"]
    for item in LEGAL_RISKS:
        lines.append(f"| {item['risk']} | {item['level']} | {item['mitigation']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线合同审阅意见。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，只做合同审阅辅助，不构成正式法律意见。

## 合同摘要

{_render_summary()}

## 关键条款

{_render_clauses()}

## 谈判建议

{_render_negotiation()}

## 法务风险

{_render_risks()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责合同摘要、关键条款、谈判建议和法务风险。
- `data.py` 可替换为真实合同管理系统、法务规则库、审批流或协同文档。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_contract_summary(query)] + extract_key_clauses(query) + LEGAL_RISKS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "合同审阅负责人", "action": item, "why": "把审阅意见转成可谈判条款。"}
        for index, item in enumerate(NEGOTIATION_POINTS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
