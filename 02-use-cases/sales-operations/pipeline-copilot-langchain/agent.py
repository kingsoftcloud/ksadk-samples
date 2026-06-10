from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import load_pipeline, recommend_followups, create_crm_actions


def ksadk_prepare_input(payload: dict, session_context: dict) -> dict:
    """把 AgentEngine 请求转换成 LangChain agent 输入。"""

    return {"input": str(payload.get("input") or "")}


# LangChain 版本展示如何用 create_agent 绑定场景工具。
root_agent = create_agent(
    model=make_langchain_chat_model(),
    tools=[load_pipeline, recommend_followups, create_crm_actions],
    system_prompt=SYSTEM_PROMPT + "\n先调用工具读取线索和跟进策略，再按线索画像、跟进策略、CRM 动作和成交风险输出。",
)
