from __future__ import annotations

from data import CANDIDATES, HIRING_RISKS, INTERVIEW_ROUNDS, JOB_PROFILE
from prompts import SYSTEM_PROMPT, TITLE


def load_job_profile(query: str) -> dict:
    """读取岗位画像。

    真实项目里这里可以替换为 JD、职级要求、团队面试标准和招聘计划。
    """

    return JOB_PROFILE


def rank_candidates(query: str) -> list[dict]:
    """按匹配度排序候选人。"""

    return sorted(CANDIDATES, key=lambda item: item["match"], reverse=True)


def plan_interviews(query: str) -> list[dict]:
    """生成面试轮次计划。"""

    return INTERVIEW_ROUNDS


def _render_job() -> str:
    must = "、".join(JOB_PROFILE["must_have"])
    nice = "、".join(JOB_PROFILE["nice_to_have"])
    return (
        f"- 岗位：{JOB_PROFILE['title']}\n"
        f"- 职级：{JOB_PROFILE['level']}\n"
        f"- 必备能力：{must}\n"
        f"- 加分项：{nice}"
    )


def _render_candidates() -> str:
    lines = ["| 候选人 | 年限 | 匹配度 | 优势 | 待追问 |", "| --- | ---: | ---: | --- | --- |"]
    for item in rank_candidates(""):
        lines.append(f"| {item['name']} | {item['years']} | {item['match']} | {item['strength']} | {item['gap']} |")
    return "\n".join(lines)


def _render_interviews() -> str:
    lines = ["| 轮次 | 重点 | 面试官 |", "| --- | --- | --- |"]
    for item in INTERVIEW_ROUNDS:
        lines.append(f"| {item['round']} | {item['focus']} | {item['interviewer']} |")
    return "\n".join(lines)


def _render_risks() -> str:
    lines = ["| 风险 | 缓解动作 |", "| --- | --- |"]
    for item in HIRING_RISKS:
        lines.append(f"| {item['risk']} | {item['mitigation']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线招聘面试计划。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实岗位 JD、ATS 和面试评价模板。

## 岗位画像

{_render_job()}

## 候选人匹配

{_render_candidates()}

## 面试计划

{_render_interviews()}

## 录用风险

{_render_risks()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责岗位画像、候选人匹配、面试计划和录用风险。
- `data.py` 可替换为真实 ATS、简历解析、日历系统或面试评价模板。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_job_profile(query)] + rank_candidates(query) + HIRING_RISKS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": item["interviewer"], "action": f"安排{item['round']}：{item['focus']}", "why": "提升面试有效性和可追溯性。"}
        for index, item in enumerate(INTERVIEW_ROUNDS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
