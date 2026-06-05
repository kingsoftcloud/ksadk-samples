from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent
from langchain_core.tools import tool

from common.memory_store import load_user_memory, save_user_memory
from common.model_config import make_langchain_chat_model


@tool
def save_memory(content: str, user_id: str = "local-user") -> dict:
    """保存一条本地记忆。"""

    return save_user_memory(user_id, content)


@tool
def load_memory(query: str = "", user_id: str = "local-user") -> dict:
    """读取本地记忆。"""

    return load_user_memory(user_id, query)


root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[save_memory, load_memory],
    system_prompt="你是 DeepAgents 记忆示例助手。用户要求记住信息时保存记忆；询问历史偏好时读取记忆。用中文回答。",
)
