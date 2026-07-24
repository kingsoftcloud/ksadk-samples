from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.kb_runtime import search_knowledge
from common.model_config import make_langchain_chat_model


# ksadk LangChain 运行时复用 LangGraph 基座；create_agent 产出 LangGraph 图。
# 知识库内容通过 ksadk_prepare_state 注入到 input，由 runner 转成消息。
def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    query = str(payload.get("input") or "")
    platform_kb = (session_context.get("kb_context") or {}).get("formatted_text") or ""
    local_or_cloud = search_knowledge(query).get("result", "")
    kb_context = f"{platform_kb}\n{local_or_cloud}".strip()
    kb_block = f"\n\n[知识库内容]\n{kb_context}" if kb_context else ""
    return {"input": f"{query}{kb_block}"}


root_agent = create_agent(
    model=make_langchain_chat_model(),
    system_prompt="你是 LangChain 知识库问答助手。只能基于提供的知识库内容回答，并标注来源。",
)

