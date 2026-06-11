from __future__ import annotations

from data import DISPATCH_ACTIONS, EQUIPMENT_STATUS, LOAD_FORECAST, SAFETY_LIMITS
from prompts import SYSTEM_PROMPT, TITLE



def load_forecast(query: str) -> dict:
    """读取负荷预测。

    真实项目里这里可以替换为 EMS、计量平台、天气服务和需求响应系统。
    """

    return LOAD_FORECAST


def inspect_equipment_status(query: str) -> list[dict]:
    """读取设备状态。"""

    return EQUIPMENT_STATUS


def plan_dispatch_actions(query: str) -> list[str]:
    """生成调度策略。"""

    return DISPATCH_ACTIONS



def _render_forecast() -> str:
    return (
        f"- 场站：{LOAD_FORECAST['site']}\n"
        f"- 周期：{LOAD_FORECAST['horizon']}\n"
        f"- 峰值：{LOAD_FORECAST['peak']}\n"
        f"- 驱动因素：{LOAD_FORECAST['driver']}"
    )


def _render_equipment() -> str:
    lines = ["| 设备 | 状态 | 信号 |", "| --- | --- | --- |"]
    for item in EQUIPMENT_STATUS:
        lines.append(f"| {item['asset']} | {item['status']} | {item['signal']} |")
    return "\n".join(lines)


def _render_dispatch() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(DISPATCH_ACTIONS, 1))


def _render_safety() -> str:
    lines = ["| 边界 | 规则 |", "| --- | --- |"]
    for item in SAFETY_LIMITS:
        lines.append(f"| {item['boundary']} | {item['rule']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为 EMS、计量平台、天气服务和需求响应系统。

## 负荷预测

{_render_forecast()}

## 设备状态

{_render_equipment()}

## 调度策略

{_render_dispatch()}

## 安全边界

{_render_safety()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责负荷预测、设备状态、调度策略和安全边界。
- `data.py` 只放公开虚构 fixture；真实接入时不得让样例直接下发控制指令。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_forecast(query)] + inspect_equipment_status(query) + SAFETY_LIMITS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "能源调度工程师", "action": item, "why": "平衡峰值负荷并保留安全冗余。"} for index, item in enumerate(DISPATCH_ACTIONS, 1)]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
