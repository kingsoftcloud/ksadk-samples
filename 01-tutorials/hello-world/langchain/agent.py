from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.model_config import make_langchain_chat_model


# ksadk LangChain 运行时复用 LangGraph 基座；create_agent 产出 LangGraph 图，
# 自带工具调用 / checkpoint / 事件流。LCEL 链 (prompt | llm | parser) 已不再支持。
def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    return {"input": str(payload.get("input") or "")}


root_agent = create_agent(
    model=make_langchain_chat_model(),
    system_prompt="你是 KSADK 的 LangChain 入门示例助手，用中文简洁回答。",
)

