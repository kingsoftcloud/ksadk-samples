from __future__ import annotations

from data import QUALITY_OVERVIEW, DEFECT_CAUSES, QUALITY_ACTIONS, VERIFICATION_METRICS
from prompts import SYSTEM_PROMPT, TITLE



def load_quality_overview(query: str) -> dict:
    """读取质量概览。

    真实项目里这里可以替换为MES、QMS、设备点检系统、工艺参数库和质量看板。
    """

    return QUALITY_OVERVIEW



def analyze_defect_causes(query: str) -> list[dict]:
    """读取并核验缺陷归因。"""

    return DEFECT_CAUSES



def plan_quality_actions(query: str) -> list[str]:
    """生成改进措施。"""

    return QUALITY_ACTIONS



def _render_summary() -> str:
    return (
        f"- 产线：{QUALITY_OVERVIEW['line']}\n"
        f"- 批次：{QUALITY_OVERVIEW['batch']}\n"
        f"- 状态：{QUALITY_OVERVIEW['status']}\n"
        f"- 关键问题：{QUALITY_OVERVIEW['key_issue']}\n"
    ).rstrip()



def _render_checks() -> str:
    lines = ["| 项目 | 状态 | 说明 |", "| --- | --- | --- |"]
    for item in DEFECT_CAUSES:
        lines.append(f"| {item['material']} | {item['status']} | {item['note']} |")
    return "\n".join(lines)



def _render_actions() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(QUALITY_ACTIONS, 1))



def _render_controls() -> str:
    lines = ["| 风险或指标 | 控制方式 |", "| --- | --- |"]
    for item in VERIFICATION_METRICS:
        lines.append(f"| {item['risk']} | {item['control']} |")
    return "\n".join(lines)



def render_demo_answer(query: str) -> str:
    """生成离线业务分析结果。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为MES、QMS、设备点检表和工艺参数库。

## 质量概览

{_render_summary()}

## 缺陷归因

{_render_checks()}

## 改进措施

{_render_actions()}

## 验证指标

{_render_controls()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责质量概览、缺陷归因、改进措施和验证指标。
- `data.py` 只放公开虚构 fixture；真实接入时必须遵守隐私保护、权限控制和人工复核边界。
""".strip()



def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return [load_quality_overview(query)] + analyze_defect_causes(query) + VERIFICATION_METRICS



def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [{"step": index, "owner": "制造质量改进工程师", "action": item, "why": "把本地 fixture 转成可执行、可审查的下一步。"} for index, item in enumerate(QUALITY_ACTIONS, 1)]



def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
