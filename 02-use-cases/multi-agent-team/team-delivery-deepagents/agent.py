from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import assign_team_roles, collect_parallel_progress


# DeepAgents 版本展示长任务协作如何通过工具组织角色和执行轨迹。
root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[assign_team_roles, collect_parallel_progress],
    system_prompt=SYSTEM_PROMPT,
)
