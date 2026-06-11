from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from tools import collect_evidence, plan_actions, render_answer


class AgentState(TypedDict):
    query: str
    evidence: list[dict]
    actions: list[dict]
    answer: str


def prepare_state(payload: dict, session_context: dict) -> AgentState:
    return {"query": str(payload.get("input") or ""), "evidence": [], "actions": [], "answer": ""}


def collect_node(state: AgentState) -> dict:
    return {"evidence": collect_evidence(state["query"])}


def plan_node(state: AgentState) -> dict:
    return {"actions": plan_actions(state["query"], state["evidence"])}


def render_node(state: AgentState) -> dict:
    return {"answer": render_answer(state["query"], state["evidence"], state["actions"])}


def build_agent_graph():
    # 标准三段式流程，便于替换成真实系统检索、计划和写回动作。
    graph = StateGraph(AgentState)
    graph.add_node("collect", collect_node)
    graph.add_node("plan", plan_node)
    graph.add_node("render", render_node)
    graph.add_edge(START, "collect")
    graph.add_edge("collect", "plan")
    graph.add_edge("plan", "render")
    graph.add_edge("render", END)
    return graph.compile()
