from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model
from prompts import SYSTEM_PROMPT
from tools import calculate_metrics, load_csv_rows


# ADK 版本展示如何把 CSV 加载和指标计算包装成工具函数。
root_agent = Agent(
    name="data_csv_insight_adk",
    model=make_adk_litellm_model(),
    description="ADK CSV 指标洞察示例。",
    instruction=SYSTEM_PROMPT + "\n先调用 load_csv_rows，再调用 calculate_metrics，最后输出数据样本、指标口径、洞察排序和图表建议。",
    tools=[load_csv_rows, calculate_metrics],
)
