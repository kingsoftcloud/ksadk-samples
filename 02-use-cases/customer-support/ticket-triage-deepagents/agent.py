from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import classify_ticket, search_support_knowledge


# DeepAgents 版本展示长任务客服排障如何通过工具组织知识检索和升级策略。
root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[search_support_knowledge, classify_ticket],
    system_prompt=SYSTEM_PROMPT,
)
