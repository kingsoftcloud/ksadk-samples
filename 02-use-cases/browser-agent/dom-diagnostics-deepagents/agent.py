from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import collect_page_observations, plan_verify_steps


# DeepAgents 版本展示长任务浏览器诊断如何通过工具组织观察和验证。
root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[collect_page_observations, plan_verify_steps],
    system_prompt=SYSTEM_PROMPT,
)
