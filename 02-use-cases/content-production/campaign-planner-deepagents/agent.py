from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import load_campaign_brief, plan_channels, draft_content


# DeepAgents 版本展示如何把场景工具交给长任务 Agent 编排。
root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[load_campaign_brief, plan_channels, draft_content],
    system_prompt=SYSTEM_PROMPT,
)
