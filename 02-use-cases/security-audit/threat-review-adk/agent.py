from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import load_change_summary, analyze_threats, plan_remediation


# ADK 版本展示如何把场景能力包装为可调用工具。
root_agent = Agent(
    name="threat_review_adk",
    model=make_adk_litellm_model(),
    description="ADK 安全审计威胁评审 Agent 示例。",
    instruction=SYSTEM_PROMPT + "\n先调用工具读取业务上下文、风险和行动建议，再按 README 中的章节输出。",
    tools=[load_change_summary, analyze_threats, plan_remediation],
)
