from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.kb_runtime import collect_kb_runtime_status, search_knowledge
from common.model_config import make_adk_litellm_model


def search_knowledge_base(query: str) -> dict:
    """检索本地或云端知识库。"""

    return search_knowledge(query)


def get_kb_runtime_status() -> dict:
    """返回当前知识库模式和有效配置。"""

    return collect_kb_runtime_status()


root_agent = Agent(
    name="knowledge_base_rag_adk",
    model=make_adk_litellm_model(),
    description="ADK 知识库 RAG 示例。",
    instruction=(
        "你是知识库问答助手。回答 KSADK、部署、知识库相关问题前，先调用 search_knowledge_base。"
        "如果用户问当前知识库配置，调用 get_kb_runtime_status。回答必须基于检索结果并标注来源。"
    ),
    tools=[search_knowledge_base, get_kb_runtime_status],
)

