from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import load_review_materials, match_policy_rules, propose_remediations


# ADK 版本展示如何把场景能力包装为可调用工具。
root_agent = Agent(
    name="compliance_policy_review_adk",
    model=make_adk_litellm_model(),
    description="ADK 合规审阅示例。",
    instruction=SYSTEM_PROMPT + "\n先调用工具读取材料和规则，再按材料清单、风险条款、整改建议和审阅记录输出。",
    tools=[load_review_materials, match_policy_rules, propose_remediations],
)
