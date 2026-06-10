from __future__ import annotations

from data import ALERTS, CHANGE_EVENTS, LOG_CLUES, POSTMORTEM_ITEMS, RUNBOOK_STEPS
from prompts import SYSTEM_PROMPT, TITLE


def collect_incident_signals(query: str) -> dict:
    """收集 incident 证据。

    默认使用本地 fixture；真实项目可以替换为 Prometheus、日志平台、Tracing 或变更系统 API。
    """

    return {"alerts": ALERTS, "logs": LOG_CLUES, "changes": CHANGE_EVENTS}


def recommend_runbook_actions(query: str) -> list[str]:
    """根据告警和线索给出处置动作。"""

    return RUNBOOK_STEPS


def _render_alerts() -> str:
    lines = ["| 指标 | 当前值 | 基线 | 窗口 | 等级 |", "| --- | ---: | ---: | --- | --- |"]
    for item in ALERTS:
        lines.append(f"| `{item['metric']}` | {item['value']} | {item['baseline']} | {item['window']} | {item['severity']} |")
    return "\n".join(lines)


def _render_clues() -> str:
    log_lines = "\n".join(f"- **{item['source']}**：{item['signal']}（{item['count']} 次）" for item in LOG_CLUES)
    change_lines = "\n".join(f"- {item['time']} `{item['service']}`：{item['event']}" for item in CHANGE_EVENTS)
    return f"### 日志线索\n\n{log_lines}\n\n### 变更事件\n\n{change_lines}"


def render_demo_answer(query: str) -> str:
    """生成离线 AIOps 告警分诊报告。"""

    action_lines = "\n".join(f"{index}. {step}" for index, step in enumerate(recommend_runbook_actions(query), 1))
    postmortem = "\n".join(f"- {item}" for item in POSTMORTEM_ITEMS)
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地 AIOps fixture，不伪造真实监控或日志结果；接入真实监控后可复用同一套分诊结构。

## 告警摘要

{_render_alerts()}

## 根因线索

{_render_clues()}

## 处置动作

{action_lines}

## 复盘事项

{postmortem}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责收集告警、日志、变更和 runbook 动作。
- `data.py` 可替换为 Prometheus、日志平台、Tracing 或变更系统。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    signals = collect_incident_signals(query)
    return signals["alerts"] + signals["logs"] + signals["changes"]


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "AIOps 值班工程师", "action": step, "why": "降低支付链路错误率和延迟。"}
        for index, step in enumerate(RUNBOOK_STEPS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
