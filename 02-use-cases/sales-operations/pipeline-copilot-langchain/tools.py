from __future__ import annotations

from data import CRM_ACTIONS, DEAL_RISKS, LEADS, PLAYBOOK
from prompts import SYSTEM_PROMPT, TITLE


def load_pipeline(query: str) -> list[dict]:
    """读取销售线索。

    真实项目里这里可以替换为 CRM 线索、商机、活动和客户画像。
    """

    return LEADS


def recommend_followups(query: str) -> list[dict]:
    """按销售阶段生成跟进策略。"""

    playbook = {item["stage"]: item["action"] for item in PLAYBOOK}
    return [{**lead, "next_action": playbook.get(lead["stage"], "安排人工复核。")} for lead in LEADS]


def create_crm_actions(query: str) -> list[str]:
    """生成 CRM 待办动作。"""

    return CRM_ACTIONS


def _render_leads() -> str:
    lines = ["| 客户 | 阶段 | 金额 | 触达间隔 | 信号 |", "| --- | --- | ---: | ---: | --- |"]
    for lead in LEADS:
        lines.append(f"| {lead['account']} | {lead['stage']} | {lead['value']} 万 | {lead['last_touch_days']} 天 | {lead['signal']} |")
    return "\n".join(lines)


def _render_followups() -> str:
    lines = ["| 客户 | 下一步 |", "| --- | --- |"]
    for item in recommend_followups(""):
        lines.append(f"| {item['account']} | {item['next_action']} |")
    return "\n".join(lines)


def _render_crm_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(CRM_ACTIONS, 1))


def _render_risks() -> str:
    lines = ["| 风险 | 影响 | 缓解动作 |", "| --- | --- | --- |"]
    for item in DEAL_RISKS:
        lines.append(f"| {item['risk']} | {item['impact']} | {item['mitigation']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线销售运营跟进计划。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实 CRM、任务系统和销售周报。

## 线索画像

{_render_leads()}

## 跟进策略

{_render_followups()}

## CRM 动作

{_render_crm_actions()}

## 成交风险

{_render_risks()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责读取 pipeline、推荐跟进、生成 CRM 动作和成交风险。
- `data.py` 可替换为真实 CRM、任务系统、客户成功系统或销售周报。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return load_pipeline(query) + recommend_followups(query) + DEAL_RISKS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "销售运营负责人", "action": item, "why": "推进下周 pipeline 跟进。"}
        for index, item in enumerate(CRM_ACTIONS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
