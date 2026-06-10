from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import collect_page_observations, plan_verify_steps


# ADK 版本展示如何把浏览器观察和验证步骤包装成工具函数。
root_agent = Agent(
    name="browser_dom_diagnostics_adk",
    model=make_adk_litellm_model(),
    description="ADK 浏览器 DOM 诊断示例。",
    instruction=SYSTEM_PROMPT + "\n先调用 collect_page_observations，再调用 plan_verify_steps，最后输出诊断报告。",
    tools=[collect_page_observations, plan_verify_steps],
)
