from __future__ import annotations

from common.scenario_runtime import ScenarioConfig, build_scenario_graph, prepare_state
from prompts import ROLE, ROUTE, SYSTEM_PROMPT, TITLE
from tools import collect_evidence, plan_actions, render_answer


def build_agent_graph():
    # 这个最佳实践版本仍然保持入口很薄，把报告生成逻辑放在 tools.py，便于替换为真实搜索或知识库。
    config = ScenarioConfig(
        name=ROUTE + '-langgraph',
        title=TITLE,
        role=ROLE,
        route=ROUTE,
        system_prompt=SYSTEM_PROMPT,
        collect_evidence=collect_evidence,
        plan_actions=plan_actions,
        render_answer=render_answer,
    )
    return build_scenario_graph(config)
