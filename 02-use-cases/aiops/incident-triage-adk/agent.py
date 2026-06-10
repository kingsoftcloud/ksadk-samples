from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import collect_incident_signals, recommend_runbook_actions


# ADK 版本展示如何把告警收集和 runbook 推荐包装成工具函数。
root_agent = Agent(
    name="aiops_incident_triage_adk",
    model=make_adk_litellm_model(),
    description="ADK AIOps 告警分诊示例。",
    instruction=SYSTEM_PROMPT + "\n先调用 collect_incident_signals，再调用 recommend_runbook_actions，最后输出告警摘要、根因线索、处置动作和复盘事项。",
    tools=[collect_incident_signals, recommend_runbook_actions],
)
