from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import list_workspace_files, plan_sandbox_commands


# ADK 版本展示如何把 Workspace/Sandbox 能力包装成明确工具。
root_agent = Agent(
    name="coding_workspace_sandbox_adk",
    model=make_adk_litellm_model(),
    description="ADK Workspace/Sandbox 编码修复示例。",
    instruction=SYSTEM_PROMPT + "\n先调用 list_workspace_files，再调用 plan_sandbox_commands，最后输出补丁计划和验证结果。",
    tools=[list_workspace_files, plan_sandbox_commands],
)
