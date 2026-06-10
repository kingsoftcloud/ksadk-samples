from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, TypedDict

from langgraph.graph import END, StateGraph


class ScenarioState(TypedDict, total=False):
    """场景 Agent 的统一状态。

    这些 demo 故意把状态字段做得直观：用户问题、路由、证据、行动项、最终答案。
    这样用户打开 Web UI 时，既能看到回答，也能顺着代码理解每个节点为什么存在。
    """

    query: str
    route: str
    evidence: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    answer: str
    session_context: dict[str, Any]


@dataclass(frozen=True)
class ScenarioConfig:
    """多文件场景工程的最小配置。

    每个场景只需要提供自己的 prompt、数据检索函数和行动生成函数；
    LangGraph 的节点编排由 `build_scenario_graph` 统一负责，避免六个 demo 复制样板代码。
    """

    name: str
    title: str
    role: str
    route: str
    system_prompt: str
    collect_evidence: Callable[[str], list[dict[str, Any]]]
    plan_actions: Callable[[str, list[dict[str, Any]]], list[dict[str, Any]]]
    render_answer: Callable[[str, list[dict[str, Any]], list[dict[str, Any]]], str]


def prepare_state(payload: dict, session_context: dict) -> ScenarioState:
    """把 AgentEngine payload 转成图状态。

    KsADK 调用 LangGraph 时会优先使用样例里的 `ksadk_prepare_state`。
    这里保留 session_context，方便后续把 workspace、memory、knowledge 等平台上下文接进来。
    """

    return {
        'query': str(payload.get('input') or '').strip() or '请演示这个场景 Agent 的能力。',
        'route': '',
        'evidence': [],
        'actions': [],
        'answer': '',
        'session_context': dict(session_context or {}),
    }


def build_scenario_graph(config: ScenarioConfig):
    """构建一个可解释、可演示的 LangGraph 场景 Agent。"""

    def classify_intent(state: ScenarioState) -> dict[str, str]:
        # 路由节点保持确定性，避免 demo 在没有模型 key 时不可运行。
        query = state.get('query', '')
        if any(word in query.lower() for word in ('status', '配置', '状态', '能力')):
            route = 'status'
        else:
            route = config.route
        return {'route': route}

    def collect_context(state: ScenarioState) -> dict[str, list[dict[str, Any]]]:
        # 证据节点模拟真实 Agent 的 retrieval/tool-call 阶段。
        return {'evidence': config.collect_evidence(state.get('query', ''))}

    def plan_next_steps(state: ScenarioState) -> dict[str, list[dict[str, Any]]]:
        # 计划节点把证据转成行动项，Web UI 中更容易看出“Agent 在做事”。
        return {'actions': config.plan_actions(state.get('query', ''), state.get('evidence', []))}

    def finalize_answer(state: ScenarioState) -> dict[str, str]:
        # 输出节点统一产出 Markdown，方便浏览器调试界面展示。
        answer = config.render_answer(
            state.get('query', ''),
            state.get('evidence', []),
            state.get('actions', []),
        )
        return {'answer': answer}

    workflow = StateGraph(ScenarioState)
    workflow.add_node('classify_intent', classify_intent)
    workflow.add_node('collect_context', collect_context)
    workflow.add_node('plan_next_steps', plan_next_steps)
    workflow.add_node('finalize_answer', finalize_answer)
    workflow.set_entry_point('classify_intent')
    workflow.add_edge('classify_intent', 'collect_context')
    workflow.add_edge('collect_context', 'plan_next_steps')
    workflow.add_edge('plan_next_steps', 'finalize_answer')
    workflow.add_edge('finalize_answer', END)
    return workflow.compile(name=config.name)
