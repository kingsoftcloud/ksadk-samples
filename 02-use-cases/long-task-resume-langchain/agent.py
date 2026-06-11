from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.model_config import make_langchain_chat_model
from tools import build_resume_payload, render_demo_answer


SYSTEM_PROMPT = """
你是长任务恢复 Agent。先调用工具读取 checkpoint、ResumeRun、tool receipt 和 CancelRun 状态，
再用中文输出 checkpoint 列表、ResumeRun、tool receipt、CancelRun 和降级说明。
不要访问真实数据库、真实 Workspace、真实 Sandbox 或私有平台。
""".strip()


def ksadk_prepare_input(payload: dict, session_context: dict) -> dict:
    # LangChain agent 入口接收 input 字段；保留 session_context 方便后续接真实 session store。
    return {"input": str(payload.get("input") or "")}


# LangChain 版本展示同一套恢复工具如何接入 create_agent。
root_agent = create_agent(
    model=make_langchain_chat_model(),
    tools=[build_resume_payload, render_demo_answer],
    system_prompt=SYSTEM_PROMPT,
)
