from __future__ import annotations

from data import ACTION_ITEMS, OPERATIONS_DATA, RISK_CONTROLS, SCENARIO_CONTEXT
from prompts import SYSTEM_PROMPT, TITLE


def load_scenario_context(query: str) -> dict:
    """读取场景上下文。

    真实项目里这里可以替换为直播中控台、商品池、库存系统、客服工单、舆情看板和转化分析平台。
    """

    return SCENARIO_CONTEXT


def inspect_operations_data(query: str) -> list[dict]:
    """读取并核验运营数据。"""

    return OPERATIONS_DATA


def plan_operational_actions(query: str) -> list[str]:
    """生成协同行动。"""

    return ACTION_ITEMS


def _render_summary() -> str:
    return (
        f"- 目标：{SCENARIO_CONTEXT['target']}\n"
        f"- 阶段：{SCENARIO_CONTEXT['stage']}\n"
        f"- 关键问题：{SCENARIO_CONTEXT['key_issue']}\n"
    ).rstrip()


def _render_checks() -> str:
    lines = ["| 项目 | 状态 | 说明 |", "| --- | --- | --- |"]
    for item in OPERATIONS_DATA:
        lines.append(f"| {item['item']} | {item['status']} | {item['note']} |")
    return "\n".join(lines)


def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(ACTION_ITEMS, 1))


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

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为直播中控台、商品池、库存系统、客服工单、舆情看板和转化分析平台。

## 直播场控

{_render_summary()}

## 商品讲解

{_render_checks()}

## 异常舆情

{_render_actions()}

## 转化复盘

{_render_controls()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责直播场控、商品讲解、异常舆情和转化复盘。
- `data.py` 只放公开虚构 fixture；真实接入时必须遵守隐私保护、权限控制和人工复核边界。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_scenario_context(query)] + inspect_operations_data(query) + RISK_CONTROLS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": '直播运营负责人', "action": item, "why": "把本地 fixture 转成可执行、可审查的下一步。"} for index, item in enumerate(ACTION_ITEMS, 1)]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
