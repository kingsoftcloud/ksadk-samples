from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model
from tools import build_resume_payload, render_demo_answer


SYSTEM_PROMPT = """
你是长任务恢复 Agent。先调用工具读取 checkpoint、ResumeRun、tool receipt 和 CancelRun 状态，
再用中文输出 checkpoint 列表、ResumeRun、tool receipt、CancelRun 和降级说明。
不要访问真实数据库、真实 Workspace、真实 Sandbox 或私有平台。
""".strip()


# DeepAgents 版本展示长任务恢复工具如何交给长任务 Agent 编排。
root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[build_resume_payload, render_demo_answer],
    system_prompt=SYSTEM_PROMPT,
)
