from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.memory_store import load_user_memory, save_user_memory
from common.model_config import make_langchain_chat_model


# ksadk LangChain 运行时复用 LangGraph 基座；create_agent 产出 LangGraph 图。
# 动态记忆通过 ksadk_prepare_state 注入到 input，由 runner 转成消息。
def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    query = str(payload.get("input") or "")
    platform_context = session_context.get("platform_context") or {}
    user_id = str(platform_context.get("user_id") or "local-user")
    if "记住" in query:
        save_user_memory(user_id, query)
    local_memory = load_user_memory(user_id, query).get("formatted_text", "")
    platform_memory = (session_context.get("memory_context") or {}).get("formatted_text") or ""
    memory = f"{platform_memory}\n{local_memory}".strip()
    memory_block = f"\n\n[可用记忆]\n{memory}" if memory else ""
    return {"input": f"{query}{memory_block}"}


root_agent = create_agent(
    model=make_langchain_chat_model(),
    system_prompt="你是 LangChain 记忆示例助手。结合提供的可用记忆回答用户问题。",
)

