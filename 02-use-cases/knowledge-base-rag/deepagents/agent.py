from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent
from langchain_core.tools import tool

from common.kb_runtime import collect_kb_runtime_status, search_knowledge
from common.model_config import make_langchain_chat_model


@tool
def search_knowledge_base(query: str) -> dict:
    """检索本地或云端知识库。"""

    return search_knowledge(query)


@tool
def get_kb_runtime_status() -> dict:
    """返回当前知识库模式和有效配置。"""

    return collect_kb_runtime_status()


root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[search_knowledge_base, get_kb_runtime_status],
    system_prompt=(
        "你是 DeepAgents 知识库问答助手。回答 KSADK、部署、知识库相关问题前，"
        "先调用 search_knowledge_base。回答必须基于检索结果并标注来源。"
    ),
)
