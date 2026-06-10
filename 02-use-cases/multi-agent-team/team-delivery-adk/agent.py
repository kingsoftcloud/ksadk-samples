from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import assign_team_roles, collect_parallel_progress


# ADK 版本展示如何把团队分工和并行轨迹包装成工具函数。
root_agent = Agent(
    name="team_delivery_adk",
    model=make_adk_litellm_model(),
    description="ADK 多 Agent 协作交付示例。",
    instruction=SYSTEM_PROMPT + "\n先调用 assign_team_roles，再调用 collect_parallel_progress，最后输出角色分工、并行轨迹、冲突合并和验收清单。",
    tools=[assign_team_roles, collect_parallel_progress],
)
