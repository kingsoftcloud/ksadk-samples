from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model


root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    system_prompt="你是 KSADK 的 DeepAgents 入门示例助手。用中文简洁回答。",
    tools=[],
)
