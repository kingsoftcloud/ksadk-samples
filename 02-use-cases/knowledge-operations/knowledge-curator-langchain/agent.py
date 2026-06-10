from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import audit_knowledge_assets, identify_knowledge_gaps, plan_knowledge_updates


def ksadk_prepare_input(payload: dict, session_context: dict) -> dict:
    """把 AgentEngine 请求转换成 LangChain agent 输入。"""

    return {"input": str(payload.get("input") or "")}


# LangChain 版本展示如何用 create_agent 绑定场景工具。
root_agent = create_agent(
    model=make_langchain_chat_model(),
    tools=[audit_knowledge_assets, identify_knowledge_gaps, plan_knowledge_updates],
    system_prompt=SYSTEM_PROMPT + "\n先调用工具盘点知识资产，再按知识盘点、缺口分析、更新计划和发布校验输出。",
)
