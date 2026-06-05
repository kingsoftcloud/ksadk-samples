from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from common.model_config import make_langchain_chat_model


def ksadk_prepare_input(payload: dict, session_context: dict) -> dict:
    return {"input": str(payload.get("input") or "")}


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是 KSADK 的 LangChain 入门示例助手，用中文简洁回答。"),
        ("human", "{input}"),
    ]
)
root_agent = prompt | make_langchain_chat_model() | StrOutputParser()

