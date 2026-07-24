from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import load_review_materials, match_policy_rules, propose_remediations


def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    """把 AgentEngine 请求转换成 LangChain agent 输入。"""

    return {"input": str(payload.get("input") or "")}


# LangChain 版本展示如何用 create_agent 绑定场景工具。
root_agent = create_agent(
    model=make_langchain_chat_model(),
    tools=[load_review_materials, match_policy_rules, propose_remediations],
    system_prompt=SYSTEM_PROMPT + "\n先调用工具读取材料和规则，再按材料清单、风险条款、整改建议和审阅记录输出。",
)
