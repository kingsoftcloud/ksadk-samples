from __future__ import annotations

from data import CASE_PROFILE, MATERIAL_CHECKS, SERVICE_COMMITMENTS, WORKFLOW_ACTIONS
from prompts import SYSTEM_PROMPT, TITLE



def load_case_profile(query: str) -> dict:
    """读取事项画像。

    真实项目里这里可以替换为政务服务平台、材料库和办件流转系统。
    """

    return CASE_PROFILE


def check_materials(query: str) -> list[dict]:
    """核验材料状态。"""

    return MATERIAL_CHECKS


def plan_workflow_actions(query: str) -> list[str]:
    """生成协同流程。"""

    return WORKFLOW_ACTIONS



def _render_profile() -> str:
    return (
        f"- 事项：{CASE_PROFILE['service']}\n"
        f"- 申请人：{CASE_PROFILE['applicant']}\n"
        f"- 状态：{CASE_PROFILE['status']}\n"
        f"- 高频卡点：{CASE_PROFILE['pain_point']}"
    )


def _render_materials() -> str:
    lines = ["| 材料 | 状态 | 说明 |", "| --- | --- | --- |"]
    for item in MATERIAL_CHECKS:
        lines.append(f"| {item['material']} | {item['status']} | {item['note']} |")
    return "\n".join(lines)


def _render_workflow() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(WORKFLOW_ACTIONS, 1))


def _render_commitments() -> str:
    lines = ["| 承诺 | 规则 |", "| --- | --- |"]
    for item in SERVICE_COMMITMENTS:
        lines.append(f"| {item['commitment']} | {item['rule']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为政务服务平台、材料库和办件流转系统。

## 事项画像

{_render_profile()}

## 材料核验

{_render_materials()}

## 协同流程

{_render_workflow()}

## 服务承诺

{_render_commitments()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责事项画像、材料核验、协同流程和服务承诺。
- `data.py` 只放公开虚构 fixture；真实接入时必须遵守隐私保护和人工复核边界。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_case_profile(query)] + check_materials(query) + SERVICE_COMMITMENTS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "政务服务协同专员", "action": item, "why": "减少重复补正并提升服务透明度。"} for index, item in enumerate(WORKFLOW_ACTIONS, 1)]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
