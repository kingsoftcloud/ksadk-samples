from __future__ import annotations

from common.scenario_runtime import ScenarioConfig, build_scenario_graph, prepare_state
from data import SCENARIO_EVIDENCE
from prompts import ROLE, ROUTE, SYSTEM_PROMPT, TITLE
from tools import collect_evidence, plan_actions, render_answer


def build_agent_graph():
    # 这里集中装配场景配置。agent.py 保持很薄，方便用户看清工程入口。
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
