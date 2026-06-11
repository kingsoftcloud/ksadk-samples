from __future__ import annotations

from data import FULFILLMENT_EXCEPTIONS, DELIVERY_RESOURCES, CUSTOMER_COMMITMENTS, REVIEW_METRICS
from prompts import SYSTEM_PROMPT, TITLE



def load_fulfillment_exceptions(query: str) -> dict:
    """读取履约异常。

    真实项目里这里可以替换为OMS、TMS、WMS、客服系统、地图服务和天气服务。
    """

    return FULFILLMENT_EXCEPTIONS



def inspect_delivery_resources(query: str) -> list[dict]:
    """读取并核验配送资源。"""

    return DELIVERY_RESOURCES



def plan_customer_commitments(query: str) -> list[str]:
    """生成客户承诺。"""

    return CUSTOMER_COMMITMENTS



def _render_summary() -> str:
    return (
        f"- 批次：{FULFILLMENT_EXCEPTIONS['batch']}\n"
        f"- 区域：{FULFILLMENT_EXCEPTIONS['region']}\n"
        f"- 状态：{FULFILLMENT_EXCEPTIONS['status']}\n"
        f"- 关键问题：{FULFILLMENT_EXCEPTIONS['key_issue']}\n"
    ).rstrip()



def _render_checks() -> str:
    lines = ["| 项目 | 状态 | 说明 |", "| --- | --- | --- |"]
    for item in DELIVERY_RESOURCES:
        lines.append(f"| {item['material']} | {item['status']} | {item['note']} |")
    return "\n".join(lines)



def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(CUSTOMER_COMMITMENTS, 1))



def _render_controls() -> str:
    lines = ["| 风险或指标 | 控制方式 |", "| --- | --- |"]
    for item in REVIEW_METRICS:
        lines.append(f"| {item['risk']} | {item['control']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为OMS、TMS、WMS、客服系统和天气服务。

## 履约异常

{_render_summary()}

## 配送资源

{_render_checks()}

## 客户承诺

{_render_actions()}

## 复盘指标

{_render_controls()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责履约异常、配送资源、客户承诺和复盘指标。
- `data.py` 只放公开虚构 fixture；真实接入时必须遵守隐私保护、权限控制和人工复核边界。
""".strip()



def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_fulfillment_exceptions(query)] + inspect_delivery_resources(query) + REVIEW_METRICS



def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "物流履约协调员", "action": item, "why": "把本地 fixture 转成可执行、可审查的下一步。"} for index, item in enumerate(CUSTOMER_COMMITMENTS, 1)]



def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
