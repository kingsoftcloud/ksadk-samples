from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import load_campaign_brief, plan_channels, draft_content


# ADK 版本展示如何把场景能力包装为可调用工具。
root_agent = Agent(
    name="content_campaign_planner_adk",
    model=make_adk_litellm_model(),
    description="ADK 内容生产传播计划示例。",
    instruction=SYSTEM_PROMPT + "\n先调用工具读取素材，再按创意简报、渠道计划、内容草稿和审核清单输出。",
    tools=[load_campaign_brief, plan_channels, draft_content],
)
