from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import list_workspace_files, plan_sandbox_commands


# DeepAgents 版本展示长任务编码修复如何通过工具接入 Workspace/Sandbox。
root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[list_workspace_files, plan_sandbox_commands],
    system_prompt=SYSTEM_PROMPT,
)
