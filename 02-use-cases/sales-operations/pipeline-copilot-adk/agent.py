from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import load_pipeline, recommend_followups, create_crm_actions


# ADK 版本展示如何把场景能力包装为可调用工具。
root_agent = Agent(
    name="sales_pipeline_copilot_adk",
    model=make_adk_litellm_model(),
    description="ADK 销售运营 Pipeline 示例。",
    instruction=SYSTEM_PROMPT + "\n先调用工具读取线索和跟进策略，再按线索画像、跟进策略、CRM 动作和成交风险输出。",
    tools=[load_pipeline, recommend_followups, create_crm_actions],
)
