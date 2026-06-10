from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import classify_ticket, search_support_knowledge


# ADK 版本展示如何把知识检索和工单分级包装成工具函数。
root_agent = Agent(
    name="support_ticket_triage_adk",
    model=make_adk_litellm_model(),
    description="ADK 客服工单分级示例。",
    instruction=SYSTEM_PROMPT + "\n先调用 search_support_knowledge，再调用 classify_ticket，最后输出工单摘要、知识匹配、处理步骤和升级策略。",
    tools=[search_support_knowledge, classify_ticket],
)
