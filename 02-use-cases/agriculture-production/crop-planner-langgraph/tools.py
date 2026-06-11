from __future__ import annotations

from data import CROP_PLAN, ENVIRONMENT_DATA, FARMING_TASKS, YIELD_FORECASTS
from prompts import SYSTEM_PROMPT, TITLE



def load_crop_plan(query: str) -> dict:
    """读取种植计划。

    真实项目里这里可以替换为农事计划系统、IoT 传感器、天气服务、农技巡检记录和采收台账。
    """

    return CROP_PLAN



def inspect_environment_data(query: str) -> list[dict]:
    """读取并核验环境数据。"""

    return ENVIRONMENT_DATA



def plan_farming_tasks(query: str) -> list[str]:
    """生成农事任务。"""

    return FARMING_TASKS



def _render_summary() -> str:
    return (
        f"- 地块：{CROP_PLAN['plot']}\n"
        f"- 作物：{CROP_PLAN['crop']}\n"
        f"- 阶段：{CROP_PLAN['stage']}\n"
        f"- 关键问题：{CROP_PLAN['key_issue']}\n"
    ).rstrip()



def _render_checks() -> str:
    lines = ["| 项目 | 状态 | 说明 |", "| --- | --- | --- |"]
    for item in ENVIRONMENT_DATA:
        lines.append(f"| {item['material']} | {item['status']} | {item['note']} |")
    return "\n".join(lines)



def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(FARMING_TASKS, 1))



def _render_controls() -> str:
    lines = ["| 风险或指标 | 控制方式 |", "| --- | --- |"]
    for item in YIELD_FORECASTS:
        lines.append(f"| {item['risk']} | {item['control']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为农事计划、传感器数据、天气服务和农技巡检记录。

## 种植计划

{_render_summary()}

## 环境数据

{_render_checks()}

## 农事任务

{_render_actions()}

## 产量预测

{_render_controls()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责种植计划、环境数据、农事任务和产量预测。
- `data.py` 只放公开虚构 fixture；真实接入时必须遵守隐私保护、权限控制和人工复核边界。
""".strip()



def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_crop_plan(query)] + inspect_environment_data(query) + YIELD_FORECASTS



def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "农业生产计划员", "action": item, "why": "把本地 fixture 转成可执行、可审查的下一步。"} for index, item in enumerate(FARMING_TASKS, 1)]



def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
