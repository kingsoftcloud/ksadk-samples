from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import load_job_profile, rank_candidates, plan_interviews


# ADK 版本展示如何把场景能力包装为可调用工具。
root_agent = Agent(
    name="hr_interview_planner_adk",
    model=make_adk_litellm_model(),
    description="ADK HR 招聘面试计划示例。",
    instruction=SYSTEM_PROMPT + "\n先调用工具读取岗位画像、候选人和面试轮次，再按岗位画像、候选人匹配、面试计划和录用风险输出。",
    tools=[load_job_profile, rank_candidates, plan_interviews],
)
