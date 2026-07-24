from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import load_job_profile, rank_candidates, plan_interviews


def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    """把 AgentEngine 请求转换成 LangChain agent 输入。"""

    return {"input": str(payload.get("input") or "")}


# LangChain 版本展示如何用 create_agent 绑定场景工具。
root_agent = create_agent(
    model=make_langchain_chat_model(),
    tools=[load_job_profile, rank_candidates, plan_interviews],
    system_prompt=SYSTEM_PROMPT + "\n先调用工具读取岗位画像、候选人和面试轮次，再按岗位画像、候选人匹配、面试计划和录用风险输出。",
)
