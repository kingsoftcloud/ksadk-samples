from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import collect_report_sources


# ADK 版本展示“工具函数 + Agent instruction”的写法，和 LangGraph 的显式节点编排互补。
root_agent = Agent(
    name="deep_research_report_writer_adk",
    model=make_adk_litellm_model(),
    description="ADK 深度研究报告生成示例。",
    instruction=SYSTEM_PROMPT + "\n回答报告类问题前，先调用 collect_report_sources 获取引用材料。",
    tools=[collect_report_sources],
)
