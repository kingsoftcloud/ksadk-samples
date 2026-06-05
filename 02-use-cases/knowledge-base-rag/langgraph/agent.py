from pathlib import Path
import sys
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from common.kb_runtime import collect_kb_runtime_status, search_knowledge
from common.model_config import make_langchain_chat_model


class AgentState(TypedDict):
    query: str
    kb_context: str
    answer: str


def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    query = str(payload.get("input") or "")
    platform_kb = (session_context.get("kb_context") or {}).get("formatted_text") or ""
    return {"query": query, "kb_context": platform_kb, "answer": ""}


def answer(state: AgentState) -> dict:
    if "配置" in state["query"] or "状态" in state["query"]:
        runtime = collect_kb_runtime_status()
        extra_context = f"知识库运行状态: {runtime}"
    else:
        extra_context = search_knowledge(state["query"]).get("result", "")
    model = make_langchain_chat_model()
    response = model.invoke(
        [
            SystemMessage(content=f"你是 LangGraph 知识库问答助手。知识库内容:\n{state['kb_context']}\n{extra_context}"),
            HumanMessage(content=state["query"]),
        ]
    )
    return {"answer": response.content}


workflow = StateGraph(AgentState)
workflow.add_node("answer", answer)
workflow.set_entry_point("answer")
workflow.add_edge("answer", END)
root_agent = workflow.compile()

