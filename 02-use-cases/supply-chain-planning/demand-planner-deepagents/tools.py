from __future__ import annotations

from data import DEMAND_FORECAST, INVENTORY_RISKS, MONITORING_METRICS, TRANSFER_PLAN
from prompts import SYSTEM_PROMPT, TITLE



def load_demand_forecast(query: str) -> dict:
    """读取需求预测。

    真实项目里这里可以替换为 ERP、WMS、OMS、渠道预测和供应商协同系统。
    """

    return DEMAND_FORECAST


def identify_inventory_risks(query: str) -> list[dict]:
    """识别库存风险。"""

    return INVENTORY_RISKS


def build_transfer_plan(query: str) -> list[str]:
    """生成调拨计划。"""

    return TRANSFER_PLAN



def _render_forecast() -> str:
    return (
        f"- 产品：{DEMAND_FORECAST['product']}\n"
        f"- 周期：{DEMAND_FORECAST['horizon']}\n"
        f"- 基线预测：{DEMAND_FORECAST['baseline']}\n"
        f"- 需求驱动：{DEMAND_FORECAST['driver']}"
    )


def _render_risks() -> str:
    lines = ["| 风险 | 等级 | 影响 |", "| --- | --- | --- |"]
    for item in INVENTORY_RISKS:
        lines.append(f"| {item['risk']} | {item['level']} | {item['impact']} |")
    return "\n".join(lines)


def _render_transfer_plan() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(TRANSFER_PLAN, 1))


def _render_metrics() -> str:
    lines = ["| 指标 | 阈值 | 负责人 |", "| --- | --- | --- |"]
    for item in MONITORING_METRICS:
        lines.append(f"| {item['metric']} | {item['threshold']} | {item['owner']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实 ERP、WMS、OMS、渠道预测和供应商协同系统。

## 需求预测

{_render_forecast()}

## 库存风险

{_render_risks()}

## 调拨计划

{_render_transfer_plan()}

## 监控指标

{_render_metrics()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责需求预测、库存风险、调拨计划和监控指标。
- `data.py` 可替换为真实 ERP、WMS、OMS、渠道预测或供应商协同系统。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_demand_forecast(query)] + identify_inventory_risks(query) + MONITORING_METRICS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "供应链计划经理", "action": item, "why": "降低缺货和积压风险。"} for index, item in enumerate(TRANSFER_PLAN, 1)]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
