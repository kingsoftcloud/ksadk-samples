from __future__ import annotations

from data import CARE_FLOW, COORDINATION_ACTIONS, OPERATION_RISKS, RESOURCE_BOTTLENECKS
from prompts import SYSTEM_PROMPT, TITLE



def load_care_flow(query: str) -> dict:
    """读取门诊流转概览。

    真实项目里这里可以替换为预约系统、排队系统和护理工作站，但公开样例只用虚构数据。
    """

    return CARE_FLOW


def find_resource_bottlenecks(query: str) -> list[dict]:
    """定位资源瓶颈。"""

    return RESOURCE_BOTTLENECKS


def plan_coordination_actions(query: str) -> list[str]:
    """生成护理协同计划。"""

    return COORDINATION_ACTIONS



def _render_flow() -> str:
    return (
        f"- 机构：{CARE_FLOW['clinic']}\n"
        f"- 时间窗：{CARE_FLOW['window']}\n"
        f"- 到诊情况：{CARE_FLOW['arrivals']}\n"
        f"- 周期时间：{CARE_FLOW['cycle_time']}"
    )


def _render_bottlenecks() -> str:
    lines = ["| 环节 | 信号 | 影响 |", "| --- | --- | --- |"]
    for item in RESOURCE_BOTTLENECKS:
        lines.append(f"| {item['area']} | {item['signal']} | {item['impact']} |")
    return "\n".join(lines)


def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(COORDINATION_ACTIONS, 1))


def _render_risks() -> str:
    lines = ["| 风险 | 等级 | 边界 |", "| --- | --- | --- |"]
    for item in OPERATION_RISKS:
        lines.append(f"| {item['risk']} | {item['level']} | {item['guardrail']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为预约、排队、护理工作站和运营看板。

## 患者流转

{_render_flow()}

## 资源瓶颈

{_render_bottlenecks()}

## 协同计划

{_render_actions()}

## 风险提醒

{_render_risks()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责患者流转、资源瓶颈、协同计划和风险提醒。
- `data.py` 只放公开虚构 fixture，真实接入时必须遵守隐私、授权和最小必要原则。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_care_flow(query)] + find_resource_bottlenecks(query) + OPERATION_RISKS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "门诊运营协调员", "action": item, "why": "缩短等待时间并降低随访遗漏风险。"} for index, item in enumerate(COORDINATION_ACTIONS, 1)]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
