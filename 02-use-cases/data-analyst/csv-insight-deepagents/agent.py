from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import calculate_metrics, load_csv_rows


# DeepAgents 版本展示长任务数据分析如何通过工具拆分数据加载和指标计算。
root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[load_csv_rows, calculate_metrics],
    system_prompt=SYSTEM_PROMPT,
)
