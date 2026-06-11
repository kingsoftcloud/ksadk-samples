from __future__ import annotations

from data import ACCEPTANCE_CHECKS, DELIVERY_ACTIONS, DELIVERY_RISKS, PROJECT_STATUS
from prompts import SYSTEM_PROMPT, TITLE


def load_project_status(query: str) -> list[dict]:
    """读取项目状态。

    真实项目里这里可以替换为项目管理系统、里程碑、风险登记表和验收流程。
    """

    return PROJECT_STATUS


def analyze_delivery_risks(query: str) -> list[dict]:
    """分析交付风险。"""

    risk_rank = {"高": 0, "中": 1, "低": 2}
    return sorted(DELIVERY_RISKS, key=lambda item: risk_rank.get(item["level"], 9))


def plan_delivery_actions(query: str) -> list[str]:
    """生成推进计划。"""

    return DELIVERY_ACTIONS


def _render_status() -> str:
    lines = ["| 模块 | 进度 | 负责人 | 当前状态 |", "| --- | ---: | --- | --- |"]
    for item in PROJECT_STATUS:
        lines.append(f"| {item['module']} | {item['progress']} | {item['owner']} | {item['status']} |")
    return "\n".join(lines)


def _render_risks() -> str:
    lines = ["| 风险 | 级别 | 影响 | 缓解动作 |", "| --- | --- | --- | --- |"]
    for item in analyze_delivery_risks(""):
        lines.append(f"| {item['risk']} | {item['level']} | {item['impact']} | {item['mitigation']} |")
    return "\n".join(lines)


def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(DELIVERY_ACTIONS, 1))


def _render_checks() -> str:
    return "\n".join(f"- [ ] {item}" for item in ACCEPTANCE_CHECKS)


def render_demo_answer(query: str) -> str:
    """生成离线项目交付计划。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实项目管理系统、风险登记表和发布审批流。

## 项目状态

{_render_status()}

## 风险雷达

{_render_risks()}

## 推进计划

{_render_actions()}

## 验收清单

{_render_checks()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责项目状态、风险雷达、推进计划和验收清单。
- `data.py` 可替换为真实项目管理系统、风险登记表、周报或发布审批流。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return load_project_status(query) + analyze_delivery_risks(query)


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "项目交付负责人", "action": item, "why": "降低交付风险并推动验收。"}
        for index, item in enumerate(DELIVERY_ACTIONS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
