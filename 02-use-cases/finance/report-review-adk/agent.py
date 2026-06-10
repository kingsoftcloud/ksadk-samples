from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import evaluate_financial_risks, load_financial_report


# ADK 版本展示如何把财务报表读取和风险评估包装成工具函数。
root_agent = Agent(
    name="finance_report_review_adk",
    model=make_adk_litellm_model(),
    description="ADK 财务报表审阅示例。",
    instruction=SYSTEM_PROMPT + "\n先调用 load_financial_report，再调用 evaluate_financial_risks，最后输出报表摘录、风险指标、异常解释和审阅结论。",
    tools=[load_financial_report, evaluate_financial_risks],
)
