from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import audit_knowledge_assets, identify_knowledge_gaps, plan_knowledge_updates


# ADK 版本展示如何把场景能力包装为可调用工具。
root_agent = Agent(
    name="knowledge_curator_adk",
    model=make_adk_litellm_model(),
    description="ADK 企业知识运营示例。",
    instruction=SYSTEM_PROMPT + "\n先调用工具盘点知识资产，再按知识盘点、缺口分析、更新计划和发布校验输出。",
    tools=[audit_knowledge_assets, identify_knowledge_gaps, plan_knowledge_updates],
)
