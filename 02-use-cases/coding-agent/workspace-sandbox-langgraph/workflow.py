from __future__ import annotations

from common.scenario_runtime import ScenarioConfig, build_scenario_graph, prepare_state
from prompts import ROLE, ROUTE, SYSTEM_PROMPT, TITLE
from tools import collect_evidence, plan_actions, render_answer


def build_agent_graph():
    # Workspace/Sandbox 版保留标准 LangGraph 四节点结构，方便用户对照替换真实工具调用。
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
