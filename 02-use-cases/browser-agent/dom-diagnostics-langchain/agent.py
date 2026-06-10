from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import collect_page_observations, plan_verify_steps


def ksadk_prepare_input(payload: dict, session_context: dict) -> dict:
    """把 AgentEngine 请求转换成 LangChain agent 输入。"""

    return {"input": str(payload.get("input") or "")}


# LangChain 版本展示如何用 create_agent 组织同一批场景工具。
root_agent = create_agent(
    model=make_langchain_chat_model(),
    tools=[collect_page_observations, plan_verify_steps],
    system_prompt=SYSTEM_PROMPT + "\n先调用 collect_page_observations，再调用 plan_verify_steps，最后输出页面观察、DOM 线索、失败诊断和验证步骤。",
)
