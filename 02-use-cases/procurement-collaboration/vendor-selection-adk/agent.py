from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import load_procurement_requests, compare_vendors, plan_negotiation


# ADK 版本展示如何把场景能力包装为可调用工具。
root_agent = Agent(
    name="procurement_vendor_selection_adk",
    model=make_adk_litellm_model(),
    description="ADK 采购协同供应商筛选示例。",
    instruction=SYSTEM_PROMPT + "\n先调用工具读取采购需求、对比供应商，再按采购需求、供应商对比、谈判计划和审批风险输出。",
    tools=[load_procurement_requests, compare_vendors, plan_negotiation],
)
