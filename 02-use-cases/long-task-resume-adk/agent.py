from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from tools import build_resume_payload, render_demo_answer


INSTRUCTION = """
你是长任务恢复 Agent。先调用工具读取 checkpoint、ResumeRun、tool receipt 和 CancelRun 状态，
再用中文输出 checkpoint 列表、ResumeRun、tool receipt、CancelRun 和降级说明。
不要访问真实数据库、真实 Workspace、真实 Sandbox 或私有平台。
""".strip()


# ADK 版本展示如何把长任务恢复能力包装为工具。
root_agent = Agent(
    name="long_task_resume_adk",
    model=make_adk_litellm_model(),
    description="ADK 长任务恢复 Agent 示例。",
    instruction=INSTRUCTION,
    tools=[build_resume_payload, render_demo_answer],
)
