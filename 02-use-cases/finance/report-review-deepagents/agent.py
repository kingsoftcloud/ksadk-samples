from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import evaluate_financial_risks, load_financial_report


# DeepAgents 版本展示长任务财务审阅如何通过工具组织报表和风险指标。
root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[load_financial_report, evaluate_financial_risks],
    system_prompt=SYSTEM_PROMPT,
)
