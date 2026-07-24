from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk import Agent

from common.model_config import make_adk_litellm_model


root_agent = Agent(
    name="hello_world_adk",
    model=make_adk_litellm_model(),
    description="最小 ADK 对话 Agent。",
    instruction="你是 KSADK 的入门示例助手。用中文简洁回答，并说明你运行在 ADK 示例中。",
)

