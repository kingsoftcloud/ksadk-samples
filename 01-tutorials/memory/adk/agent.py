from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.memory_store import load_user_memory, save_user_memory
from common.model_config import make_adk_litellm_model


def save_memory(content: str, user_id: str = "local-user") -> dict:
    """保存一条本地记忆。"""

    return save_user_memory(user_id, content)


def load_memory(query: str = "", user_id: str = "local-user") -> dict:
    """读取本地记忆。"""

    return load_user_memory(user_id, query)


root_agent = Agent(
    name="memory_adk",
    model=make_adk_litellm_model(),
    description="ADK 记忆示例。",
    instruction="你是记忆示例助手。用户要求记住信息时调用 save_memory；用户询问历史偏好时调用 load_memory。用中文回答。",
    tools=[save_memory, load_memory],
)

