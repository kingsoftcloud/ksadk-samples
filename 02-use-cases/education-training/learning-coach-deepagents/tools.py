from __future__ import annotations

from data import ASSESSMENTS, LEARNER_PROFILE, SKILL_GAPS, TRAINING_PLAN
from prompts import SYSTEM_PROMPT, TITLE



def load_learner_profile(query: str) -> dict:
    """读取学习画像。

    真实项目里这里可以替换为 LMS、练习平台、测评系统和学习档案。
    """

    return LEARNER_PROFILE


def diagnose_skill_gaps(query: str) -> list[dict]:
    """诊断能力缺口。"""

    return SKILL_GAPS


def build_training_plan(query: str) -> list[str]:
    """生成训练计划。"""

    return TRAINING_PLAN



def _render_profile() -> str:
    return (
        f"- 学员：{LEARNER_PROFILE['learner']}\n"
        f"- 目标：{LEARNER_PROFILE['goal']}\n"
        f"- 当前水平：{LEARNER_PROFILE['level']}\n"
        f"- 学习偏好：{LEARNER_PROFILE['preference']}"
    )


def _render_gaps() -> str:
    lines = ["| 知识点 | 证据 | 优先级 |", "| --- | --- | --- |"]
    for item in SKILL_GAPS:
        lines.append(f"| {item['topic']} | {item['evidence']} | {item['priority']} |")
    return "\n".join(lines)


def _render_plan() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(TRAINING_PLAN, 1))


def _render_assessments() -> str:
    lines = ["| 方式 | 指标 |", "| --- | --- |"]
    for item in ASSESSMENTS:
        lines.append(f"| {item['method']} | {item['metric']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实 LMS、练习平台、测评系统和学习档案。

## 学习画像

{_render_profile()}

## 能力缺口

{_render_gaps()}

## 训练计划

{_render_plan()}

## 评估方式

{_render_assessments()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责学习画像、能力缺口、训练计划和评估方式。
- `data.py` 可替换为真实 LMS、练习平台、测评系统或学习档案。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_learner_profile(query)] + diagnose_skill_gaps(query) + ASSESSMENTS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "学习教练", "action": item, "why": "把能力缺口转成可跟踪训练动作。"} for index, item in enumerate(TRAINING_PLAN, 1)]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
