from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import evaluate_financial_risks, load_financial_report


def ksadk_prepare_input(payload: dict, session_context: dict) -> dict:
    """把 AgentEngine 请求转换成 LangChain agent 输入。"""

    return {"input": str(payload.get("input") or "")}


# LangChain 版本展示如何用 create_agent 绑定财务审阅工具。
root_agent = create_agent(
    model=make_langchain_chat_model(),
    tools=[load_financial_report, evaluate_financial_risks],
    system_prompt=SYSTEM_PROMPT + "\n先调用 load_financial_report，再调用 evaluate_financial_risks，最后输出报表摘录、风险指标、异常解释和审阅结论。",
)
