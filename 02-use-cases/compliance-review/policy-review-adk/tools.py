from __future__ import annotations

from data import MATERIALS, POLICY_RULES, REMEDIATIONS, REVIEW_LOG
from prompts import SYSTEM_PROMPT, TITLE


def load_review_materials(query: str) -> list[dict]:
    """读取待审阅材料。

    真实项目里这里可以替换为 Workspace 文档、CMS 草稿或审批系统附件。
    """

    return MATERIALS


def match_policy_rules(query: str) -> list[dict]:
    """匹配合规规则。"""

    return POLICY_RULES


def propose_remediations(query: str) -> list[str]:
    """生成整改建议。"""

    return REMEDIATIONS


def _render_materials() -> str:
    lines = ["| 材料 ID | 标题 | 负责人 | 关键表述 |", "| --- | --- | --- | --- |"]
    for item in MATERIALS:
        lines.append(f"| `{item['id']}` | {item['title']} | {item['owner']} | {item['claim']} |")
    return "\n".join(lines)


def _render_rules() -> str:
    lines = ["| 规则 | 等级 | 风险 |", "| --- | --- | --- |"]
    for item in POLICY_RULES:
        lines.append(f"| {item['rule']} | {item['severity']} | {item['risk']} |")
    return "\n".join(lines)


def _render_remediations() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(REMEDIATIONS, 1))


def _render_log() -> str:
    return "\n".join(f"- **{item['step']}**：{item['result']}" for item in REVIEW_LOG)


def render_demo_answer(query: str) -> str:
    """生成离线合规审阅报告。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实 Workspace 文档、法务规则库和审计记录。

## 材料清单

{_render_materials()}

## 风险条款

{_render_rules()}

## 整改建议

{_render_remediations()}

## 审阅记录

{_render_log()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责材料读取、规则匹配、整改建议和审阅记录。
- `data.py` 可替换为真实 Workspace、CMS、合规规则库或审批流。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return load_review_materials(query) + match_policy_rules(query)


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "合规审阅负责人", "action": item, "why": "降低对外发布材料的事实、竞品和脱敏风险。"}
        for index, item in enumerate(REMEDIATIONS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
