from pathlib import Path
import sys
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from common.memory_store import load_user_memory, save_user_memory
from common.model_config import make_langchain_chat_model


class AgentState(TypedDict):
    query: str
    user_id: str
    memory_context: str
    answer: str


def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    platform_context = session_context.get("platform_context") or {}
    user_id = str(platform_context.get("user_id") or "local-user")
    query = str(payload.get("input") or "")
    return {
        "query": query,
        "user_id": user_id,
        "memory_context": str((session_context.get("memory_context") or {}).get("formatted_text") or ""),
        "answer": "",
    }


def answer(state: AgentState) -> dict:
    query = state["query"]
    if "记住" in query:
        save_user_memory(state["user_id"], query)
    local_memory = load_user_memory(state["user_id"], query).get("formatted_text", "")
    model = make_langchain_chat_model()
    response = model.invoke(
        [
            SystemMessage(content=f"你是 LangGraph 记忆示例助手。已有记忆:\n{state['memory_context']}\n{local_memory}"),
            HumanMessage(content=query),
        ]
    )
    return {"answer": response.content}


workflow = StateGraph(AgentState)
workflow.add_node("answer", answer)
workflow.add_edge(START, "answer")
workflow.add_edge("answer", END)
root_agent = workflow.compile()

