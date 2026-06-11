from __future__ import annotations

from data import EXPERIMENT_SUMMARY, OPTIMIZATION_ACTIONS, REVIEW_METRICS, USER_SEGMENTS
from prompts import SYSTEM_PROMPT, TITLE


def load_experiment_summary(query: str) -> dict:
    """读取产品实验摘要。

    真实项目里这里可以替换为 A/B 实验、埋点漏斗和增长分析平台。
    """

    return EXPERIMENT_SUMMARY


def segment_users(query: str) -> list[dict]:
    """生成用户分群。"""

    return USER_SEGMENTS


def plan_optimization_actions(query: str) -> list[str]:
    """生成运营优化动作。"""

    return OPTIMIZATION_ACTIONS


def _render_summary() -> str:
    return (
        f"- 实验：{EXPERIMENT_SUMMARY['name']}\n"
        f"- 目标：{EXPERIMENT_SUMMARY['goal']}\n"
        f"- 样本：{EXPERIMENT_SUMMARY['sample']}\n"
        f"- 结果：{EXPERIMENT_SUMMARY['result']}"
    )


def _render_segments() -> str:
    lines = ["| 用户分群 | 占比 | 行为信号 | 运营机会 |", "| --- | ---: | --- | --- |"]
    for item in USER_SEGMENTS:
        lines.append(f"| {item['segment']} | {item['size']} | {item['signal']} | {item['opportunity']} |")
    return "\n".join(lines)


def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(OPTIMIZATION_ACTIONS, 1))


def _render_metrics() -> str:
    lines = ["| 指标 | 基线 | 目标 |", "| --- | ---: | ---: |"]
    for item in REVIEW_METRICS:
        lines.append(f"| {item['metric']} | {item['baseline']} | {item['target']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线产品实验复盘。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实埋点、实验平台和运营触达系统。

## 实验概览

{_render_summary()}

## 用户分群

{_render_segments()}

## 优化动作

{_render_actions()}

## 复盘指标

{_render_metrics()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责实验概览、用户分群、优化动作和复盘指标。
- `data.py` 可替换为真实 A/B 实验、埋点、增长分析或运营触达系统。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_experiment_summary(query)] + segment_users(query) + REVIEW_METRICS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "产品运营负责人", "action": item, "why": "提升实验转化并避免单指标优化。"}
        for index, item in enumerate(OPTIMIZATION_ACTIONS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
