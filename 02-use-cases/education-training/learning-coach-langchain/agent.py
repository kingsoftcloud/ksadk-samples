from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from common.model_config import make_langchain_chat_model
from prompts import SYSTEM_PROMPT
from tools import load_learner_profile, diagnose_skill_gaps, build_training_plan


def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    # LangChain agent 入口接收 input 字段；保留 session_context 方便后续接 workspace/memory。
    return {"input": str(payload.get("input") or "")}


# LangChain 版本展示同一批工具如何接入 create_agent。
root_agent = create_agent(
    model=make_langchain_chat_model(),
    tools=[load_learner_profile, diagnose_skill_gaps, build_training_plan],
    system_prompt=SYSTEM_PROMPT + "\n输出必须包含 README 中列出的四个业务章节。",
)
