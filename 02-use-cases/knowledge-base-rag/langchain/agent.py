from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from common.kb_runtime import search_knowledge
from common.model_config import make_langchain_chat_model


def ksadk_prepare_input(payload: dict, session_context: dict) -> dict:
    query = str(payload.get("input") or "")
    platform_kb = (session_context.get("kb_context") or {}).get("formatted_text") or ""
    local_or_cloud = search_knowledge(query).get("result", "")
    return {"input": query, "kb_context": f"{platform_kb}\n{local_or_cloud}".strip()}


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是 LangChain 知识库问答助手。只能基于知识库内容回答，并标注来源。\n\n知识库内容:\n{kb_context}"),
        ("human", "{input}"),
    ]
)
root_agent = prompt | make_langchain_chat_model() | StrOutputParser()

