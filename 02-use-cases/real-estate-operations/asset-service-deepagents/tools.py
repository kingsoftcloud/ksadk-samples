from __future__ import annotations

from data import ASSET_STATUS, TENANT_SERVICES, WORK_ORDER_ACTIONS, REVENUE_RISKS
from prompts import SYSTEM_PROMPT, TITLE



def load_asset_status(query: str) -> dict:
    """读取资产状态。

    真实项目里这里可以替换为资产台账、租户服务台、工单系统、合同管理系统和财务看板。
    """

    return ASSET_STATUS



def inspect_tenant_services(query: str) -> list[dict]:
    """读取并核验租户服务。"""

    return TENANT_SERVICES



def plan_work_order_actions(query: str) -> list[str]:
    """生成工单协同。"""

    return WORK_ORDER_ACTIONS



def _render_summary() -> str:
    return (
        f"- 资产：{ASSET_STATUS['asset']}\n"
        f"- 周期：{ASSET_STATUS['period']}\n"
        f"- 状态：{ASSET_STATUS['status']}\n"
        f"- 关键问题：{ASSET_STATUS['key_issue']}\n"
    ).rstrip()



def _render_checks() -> str:
    lines = ["| 项目 | 状态 | 说明 |", "| --- | --- | --- |"]
    for item in TENANT_SERVICES:
        lines.append(f"| {item['material']} | {item['status']} | {item['note']} |")
    return "\n".join(lines)



def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(WORK_ORDER_ACTIONS, 1))



def _render_controls() -> str:
    lines = ["| 风险或指标 | 控制方式 |", "| --- | --- |"]
    for item in REVENUE_RISKS:
        lines.append(f"| {item['risk']} | {item['control']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为资产台账、租户服务台、工单系统和合同管理系统。

## 资产状态

{_render_summary()}

## 租户服务

{_render_checks()}

## 工单协同

{_render_actions()}

## 收益风险

{_render_controls()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责资产状态、租户服务、工单协同和收益风险。
- `data.py` 只放公开虚构 fixture；真实接入时必须遵守隐私保护、权限控制和人工复核边界。
""".strip()



def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_asset_status(query)] + inspect_tenant_services(query) + REVENUE_RISKS



def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "园区资产运营经理", "action": item, "why": "把本地 fixture 转成可执行、可审查的下一步。"} for index, item in enumerate(WORK_ORDER_ACTIONS, 1)]



def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
