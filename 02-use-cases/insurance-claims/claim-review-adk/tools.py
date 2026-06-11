from __future__ import annotations

from data import CLAIM_SUMMARY, MATERIAL_CHECKS, REVIEW_ACTIONS, RISK_CONTROLS
from prompts import SYSTEM_PROMPT, TITLE



def load_claim_summary(query: str) -> dict:
    """读取案件摘要。

    真实项目里这里可以替换为理赔系统、影像件库、定损系统、风控规则库和人工审核工作台。
    """

    return CLAIM_SUMMARY



def verify_claim_materials(query: str) -> list[dict]:
    """读取并核验材料核验。"""

    return MATERIAL_CHECKS



def plan_review_actions(query: str) -> list[str]:
    """生成审核建议。"""

    return REVIEW_ACTIONS



def _render_summary() -> str:
    return (
        f"- 类型：{CLAIM_SUMMARY['claim_type']}\n"
        f"- 申请人：{CLAIM_SUMMARY['claimant']}\n"
        f"- 阶段：{CLAIM_SUMMARY['stage']}\n"
        f"- 关键问题：{CLAIM_SUMMARY['key_issue']}\n"
    ).rstrip()



def _render_checks() -> str:
    lines = ["| 项目 | 状态 | 说明 |", "| --- | --- | --- |"]
    for item in MATERIAL_CHECKS:
        lines.append(f"| {item['material']} | {item['status']} | {item['note']} |")
    return "\n".join(lines)



def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(REVIEW_ACTIONS, 1))



def _render_controls() -> str:
    lines = ["| 风险或指标 | 控制方式 |", "| --- | --- |"]
    for item in RISK_CONTROLS:
        lines.append(f"| {item['risk']} | {item['control']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为理赔系统、影像件库、定损系统和风控规则库。

## 案件摘要

{_render_summary()}

## 材料核验

{_render_checks()}

## 审核建议

{_render_actions()}

## 风险控制

{_render_controls()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责案件摘要、材料核验、审核建议和风险控制。
- `data.py` 只放公开虚构 fixture；真实接入时必须遵守隐私保护、权限控制和人工复核边界。
""".strip()



def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_claim_summary(query)] + verify_claim_materials(query) + RISK_CONTROLS



def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "理赔审核协同专员", "action": item, "why": "把本地 fixture 转成可执行、可审查的下一步。"} for index, item in enumerate(REVIEW_ACTIONS, 1)]



def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
