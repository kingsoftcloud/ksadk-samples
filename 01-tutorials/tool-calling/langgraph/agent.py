from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import Annotated, TypedDict

from common.model_config import make_langchain_chat_model


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def calculate(expression: str) -> dict:
    """计算简单数学表达式。"""

    try:
        return {"status": "success", "result": eval(expression, {"__builtins__": {}}, {})}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@tool
def get_weather(city: str) -> dict:
    """查询示例天气数据。"""

    data = {"北京": "晴，25°C", "上海": "多云，28°C", "深圳": "阵雨，30°C", "广州": "雷阵雨，31°C"}
    return {"city": city, "weather": data.get(city, "暂无示例天气数据")}


tools = [calculate, get_weather]
model = make_langchain_chat_model().bind_tools(tools)


def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    return {
        "messages": [
            SystemMessage(content="你是 LangGraph 工具调用示例助手。需要时调用工具，用中文回答。"),
            HumanMessage(content=str(payload.get("input") or "")),
        ]
    }


def call_model(state: AgentState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else END


workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")
root_agent = workflow.compile()

