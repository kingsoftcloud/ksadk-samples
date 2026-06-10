from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import ksadk_prepare_state, root_agent


DEMO_QUESTION = '分析这个月 Agent 调试功能的使用趋势。'


if __name__ == "__main__":
    # 这个脚本用于 README 和 CI smoke：不启动 Web UI，也不需要模型 key。
    state = ksadk_prepare_state({"input": DEMO_QUESTION}, {})
    result = root_agent.invoke(state)
    print(result["answer"])
