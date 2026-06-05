from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from common.memory_store import load_user_memory, save_user_memory
from common.model_config import make_langchain_chat_model


def ksadk_prepare_input(payload: dict, session_context: dict) -> dict:
    query = str(payload.get("input") or "")
    platform_context = session_context.get("platform_context") or {}
    user_id = str(platform_context.get("user_id") or "local-user")
    if "记住" in query:
        save_user_memory(user_id, query)
    local_memory = load_user_memory(user_id, query).get("formatted_text", "")
    platform_memory = (session_context.get("memory_context") or {}).get("formatted_text") or ""
    return {"input": query, "memory": f"{platform_memory}\n{local_memory}".strip()}


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是 LangChain 记忆示例助手。可用记忆:\n{memory}"),
        ("human", "{input}"),
    ]
)
root_agent = prompt | make_langchain_chat_model() | StrOutputParser()

