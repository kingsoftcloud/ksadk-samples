from __future__ import annotations

from data import CUSTOMER_HEALTH, FOLLOW_UPS, RISK_SIGNALS, SUCCESS_ACTIONS
from prompts import SYSTEM_PROMPT, TITLE



def load_customer_health(query: str) -> dict:
    """读取客户健康画像。

    真实项目里这里可以替换为 CRM、产品埋点、续费系统和客户旅程平台。
    """

    return CUSTOMER_HEALTH


def detect_risk_signals(query: str) -> list[dict]:
    """识别客户风险信号。"""

    return RISK_SIGNALS


def plan_success_actions(query: str) -> list[str]:
    """生成客户成功行动计划。"""

    return SUCCESS_ACTIONS



def _render_health() -> str:
    return (
        f"- 客户：{CUSTOMER_HEALTH['customer']}\n"
        f"- 健康分：{CUSTOMER_HEALTH['health_score']}\n"
        f"- 阶段：{CUSTOMER_HEALTH['stage']}\n"
        f"- 使用情况：{CUSTOMER_HEALTH['usage']}\n"
        f"- 价值达成：{CUSTOMER_HEALTH['value']}"
    )


def _render_risks() -> str:
    lines = ["| 风险信号 | 等级 | 原因 |", "| --- | --- | --- |"]
    for item in RISK_SIGNALS:
        lines.append(f"| {item['signal']} | {item['level']} | {item['reason']} |")
    return "\n".join(lines)


def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(SUCCESS_ACTIONS, 1))


def _render_follow_ups() -> str:
    lines = ["| 节奏 | 负责人 | 检查点 |", "| --- | --- | --- |"]
    for item in FOLLOW_UPS:
        lines.append(f"| {item['cadence']} | {item['owner']} | {item['checkpoint']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实 CRM、产品埋点、续费系统和客户旅程平台。

## 客户健康

{_render_health()}

## 风险信号

{_render_risks()}

## 成功计划

{_render_actions()}

## 跟进节奏

{_render_follow_ups()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责客户健康、风险信号、成功计划和跟进节奏。
- `data.py` 可替换为真实 CRM、产品埋点、续费系统或客户旅程平台。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_customer_health(query)] + detect_risk_signals(query) + FOLLOW_UPS


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "客户成功经理", "action": item, "why": "降低续费风险并提升客户价值感知。"} for index, item in enumerate(SUCCESS_ACTIONS, 1)]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
