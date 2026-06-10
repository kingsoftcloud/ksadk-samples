from __future__ import annotations

from common.scenario_runtime import ScenarioConfig, build_scenario_graph, prepare_state
from prompts import ROLE, SYSTEM_PROMPT, TITLE
from tools import collect_evidence, plan_actions, render_answer


def build_agent_graph():
    # LangGraph 版本复用通用场景编排，把差异收敛到 tools.py 和 data.py。
    config = ScenarioConfig(
        name="campaign-planner-langgraph",
        title=TITLE,
        role=ROLE,
        route="campaign-planner",
        system_prompt=SYSTEM_PROMPT,
        collect_evidence=collect_evidence,
        plan_actions=plan_actions,
        render_answer=render_answer,
    )
    return build_scenario_graph(config)
