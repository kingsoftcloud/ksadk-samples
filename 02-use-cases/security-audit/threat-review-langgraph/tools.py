from __future__ import annotations

from data import CHANGE_SUMMARY, EVIDENCE_ITEMS, REMEDIATION_PLAN, THREATS
from prompts import SYSTEM_PROMPT, TITLE


def load_change_summary(query: str) -> dict:
    """读取安全变更摘要。

    真实项目里这里可以替换为变更单、架构图、接口和资产清单。
    """

    return CHANGE_SUMMARY


def analyze_threats(query: str) -> list[dict]:
    """分析威胁和控制项。"""

    severity_rank = {"高": 0, "中": 1, "低": 2}
    return sorted(THREATS, key=lambda item: severity_rank.get(item["severity"], 9))


def plan_remediation(query: str) -> list[str]:
    """生成整改计划。"""

    return REMEDIATION_PLAN


def _render_summary() -> str:
    return (
        f"- 变更：{CHANGE_SUMMARY['change']}\n"
        f"- 范围：{CHANGE_SUMMARY['scope']}\n"
        f"- 资产：{CHANGE_SUMMARY['assets']}\n"
        f"- 暴露面：{CHANGE_SUMMARY['exposure']}"
    )


def _render_threats() -> str:
    lines = ["| 威胁 | 严重度 | 影响 | 控制措施 |", "| --- | --- | --- | --- |"]
    for item in analyze_threats(""):
        lines.append(f"| {item['threat']} | {item['severity']} | {item['impact']} | {item['control']} |")
    return "\n".join(lines)


def _render_plan() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(REMEDIATION_PLAN, 1))


def _render_evidence() -> str:
    lines = ["| 证据 | 状态 | Owner |", "| --- | --- | --- |"]
    for item in EVIDENCE_ITEMS:
        lines.append(f"| {item['evidence']} | {item['status']} | {item['owner']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线安全威胁评审。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，只演示安全评审流程，不包含真实漏洞或生产环境细节。

## 变更摘要

{_render_summary()}

## 威胁分析

{_render_threats()}

## 整改计划

{_render_plan()}

## 验证证据

{_render_evidence()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责变更摘要、威胁分析、整改计划和验证证据。
- `data.py` 可替换为真实变更单、安全扫描、权限审计、发布审批或风险台账。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_change_summary(query)] + analyze_threats(query) + EVIDENCE_ITEMS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "安全审计负责人", "action": item, "why": "降低发布前安全风险并留下审计证据。"}
        for index, item in enumerate(REMEDIATION_PLAN, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
