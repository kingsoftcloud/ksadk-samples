from __future__ import annotations

from data import EXPLANATION_NOTES, REPORT_ROWS, REVIEW_ACTIONS, RISK_THRESHOLDS
from prompts import SYSTEM_PROMPT, TITLE


def load_financial_report(query: str) -> list[dict]:
    """加载财务报表摘录。

    默认使用本地 fixture；真实项目可以替换为 Workspace Excel、财务系统 API 或审计数据集。
    """

    return REPORT_ROWS


def evaluate_financial_risks(query: str) -> list[dict]:
    """根据阈值和趋势评估风险指标。"""

    latest = REPORT_ROWS[-1]
    previous = REPORT_ROWS[-2]
    revenue_growth = latest["revenue"] / previous["revenue"] - 1
    cashflow_growth = latest["operating_cashflow"] / previous["operating_cashflow"] - 1
    margin_drop = previous["gross_margin"] - latest["gross_margin"]
    return [
        {"name": "收入增长", "value": f"{revenue_growth * 100:.1f}%", "assessment": "收入继续增长，但需要拆解客户和回款质量。"},
        {"name": "毛利率下降", "value": f"{margin_drop * 100:.1f} 个百分点", "assessment": "触发毛利率连续下滑关注项。"},
        {"name": "现金流增速", "value": f"{cashflow_growth * 100:.1f}%", "assessment": "现金流显著弱于收入增长。"},
        {"name": "应收账款天数", "value": f"{latest['ar_days']} 天", "assessment": "超过 60 天阈值，应进入专项跟踪。"},
    ]


def _render_report_table() -> str:
    lines = ["| 季度 | 收入 | 毛利率 | 经营现金流 | 应收账款天数 |", "| --- | ---: | ---: | ---: | ---: |"]
    for row in REPORT_ROWS:
        lines.append(
            f"| {row['quarter']} | {row['revenue']} | {row['gross_margin'] * 100:.1f}% | {row['operating_cashflow']} | {row['ar_days']} |"
        )
    return "\n".join(lines)


def _render_risk_table(risks: list[dict]) -> str:
    lines = ["| 指标 | 数值 | 判断 |", "| --- | ---: | --- |"]
    for item in risks:
        lines.append(f"| {item['name']} | {item['value']} | {item['assessment']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线财务审阅报告。"""

    risks = evaluate_financial_risks(query)
    threshold_lines = "\n".join(f"- **{item['name']}**：{item['rule']}（等级：{item['severity']}）" for item in RISK_THRESHOLDS)
    explanation = "\n".join(f"- {item}" for item in EXPLANATION_NOTES)
    actions = "\n".join(f"{index}. {item}" for index, item in enumerate(REVIEW_ACTIONS, 1))
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地财务 fixture，不伪造真实企业数据或审计意见；接入真实报表后可复用同一套审阅结构。

## 报表摘录

{_render_report_table()}

## 风险指标

{threshold_lines}

{_render_risk_table(risks)}

## 异常解释

{explanation}

## 审阅结论

{actions}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责读取报表、计算风险和渲染审阅结论。
- `data.py` 可替换为 Workspace Excel、财务系统 API 或审计数据集。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return load_financial_report(query) + evaluate_financial_risks(query)


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "财务分析师", "action": action, "why": "提升收入、利润和现金流审阅的可追溯性。"}
        for index, action in enumerate(REVIEW_ACTIONS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
