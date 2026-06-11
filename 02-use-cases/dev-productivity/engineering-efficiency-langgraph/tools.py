from __future__ import annotations

from data import BOTTLENECKS, IMPROVEMENT_PLAN, METRICS, TEAM_OVERVIEW
from prompts import SYSTEM_PROMPT, TITLE


def load_team_overview(query: str) -> dict:
    """读取研发团队概览。

    真实项目里这里可以替换为 Git、CI、Issue、代码评审和发布流水线数据。
    """

    return TEAM_OVERVIEW


def analyze_bottlenecks(query: str) -> list[dict]:
    """分析效能瓶颈。"""

    return BOTTLENECKS


def plan_improvements(query: str) -> list[str]:
    """生成效能改进计划。"""

    return IMPROVEMENT_PLAN


def _render_overview() -> str:
    return (
        f"- 团队：{TEAM_OVERVIEW['team']}\n"
        f"- 迭代：{TEAM_OVERVIEW['sprint']}\n"
        f"- 吞吐：{TEAM_OVERVIEW['throughput']}\n"
        f"- 质量：{TEAM_OVERVIEW['quality']}\n"
        f"- 交付：{TEAM_OVERVIEW['delivery']}"
    )


def _render_bottlenecks() -> str:
    lines = ["| 领域 | 信号 | 影响 | 改进方向 |", "| --- | --- | --- | --- |"]
    for item in analyze_bottlenecks(""):
        lines.append(f"| {item['area']} | {item['signal']} | {item['impact']} | {item['fix']} |")
    return "\n".join(lines)


def _render_plan() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(IMPROVEMENT_PLAN, 1))


def _render_metrics() -> str:
    lines = ["| 指标 | 目标 | 价值 |", "| --- | --- | --- |"]
    for item in METRICS:
        lines.append(f"| {item['metric']} | {item['target']} | {item['why']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线研发效能改进计划。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实 Git、CI、Issue、评审和发布流水线数据。

## 研发概览

{_render_overview()}

## 瓶颈分析

{_render_bottlenecks()}

## 改进计划

{_render_plan()}

## 度量指标

{_render_metrics()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责研发概览、瓶颈分析、改进计划和度量指标。
- `data.py` 可替换为真实 Git、CI、Issue、评审、发布或研发效能平台数据。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_team_overview(query)] + analyze_bottlenecks(query) + METRICS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "研发效能负责人", "action": item, "why": "减少等待、返工和发布风险。"}
        for index, item in enumerate(IMPROVEMENT_PLAN, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
