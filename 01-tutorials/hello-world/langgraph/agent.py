from pathlib import Path
import sys
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from common.model_config import make_langchain_chat_model


class AgentState(TypedDict):
    query: str
    answer: str


def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    return {
        "query": str(payload.get("input") or ""),
        "answer": "",
        "platform_context": session_context.get("platform_context"),
    }


def answer(state: AgentState) -> dict:
    model = make_langchain_chat_model()
    response = model.invoke(
        [
            SystemMessage(content="你是 KSADK 的 LangGraph 入门示例助手，用中文简洁回答。"),
            HumanMessage(content=state["query"]),
        ]
    )
    return {"answer": response.content}


workflow = StateGraph(AgentState)
workflow.add_node("answer", answer)
workflow.add_edge(START, "answer")
workflow.add_edge("answer", END)
root_agent = workflow.compile()

