from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import collect_report_sources


# DeepAgents 版本展示“工具 + 长任务系统提示词”的写法。
root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[collect_report_sources],
    system_prompt=SYSTEM_PROMPT,
)
