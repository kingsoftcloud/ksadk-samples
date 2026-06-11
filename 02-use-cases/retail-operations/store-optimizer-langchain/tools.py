from __future__ import annotations

from data import STORE_PERFORMANCE, INVENTORY_MIX, RETAIL_ACTIONS, REVIEW_METRICS
from prompts import SYSTEM_PROMPT, TITLE



def load_store_performance(query: str) -> dict:
    """读取门店表现。

    真实项目里这里可以替换为POS、WMS、商品主数据、促销系统、会员分析和门店任务看板。
    """

    return STORE_PERFORMANCE



def inspect_inventory_mix(query: str) -> list[dict]:
    """读取并核验库存结构。"""

    return INVENTORY_MIX



def plan_retail_actions(query: str) -> list[str]:
    """生成运营动作。"""

    return RETAIL_ACTIONS



def _render_summary() -> str:
    return (
        f"- 门店：{STORE_PERFORMANCE['store']}\n"
        f"- 周期：{STORE_PERFORMANCE['period']}\n"
        f"- 状态：{STORE_PERFORMANCE['status']}\n"
        f"- 关键问题：{STORE_PERFORMANCE['key_issue']}\n"
    ).rstrip()



def _render_checks() -> str:
    lines = ["| 项目 | 状态 | 说明 |", "| --- | --- | --- |"]
    for item in INVENTORY_MIX:
        lines.append(f"| {item['material']} | {item['status']} | {item['note']} |")
    return "\n".join(lines)



def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(RETAIL_ACTIONS, 1))



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

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为POS、WMS、商品主数据、促销系统和门店排班表。

## 门店表现

{_render_summary()}

## 库存结构

{_render_checks()}

## 运营动作

{_render_actions()}

## 复盘指标

{_render_controls()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责门店表现、库存结构、运营动作和复盘指标。
- `data.py` 只放公开虚构 fixture；真实接入时必须遵守隐私保护、权限控制和人工复核边界。
""".strip()



def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_store_performance(query)] + inspect_inventory_mix(query) + REVIEW_METRICS



def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "零售运营优化顾问", "action": item, "why": "把本地 fixture 转成可执行、可审查的下一步。"} for index, item in enumerate(RETAIL_ACTIONS, 1)]



def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
