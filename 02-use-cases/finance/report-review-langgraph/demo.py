from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import ksadk_prepare_state, root_agent


DEMO_QUESTION = "审阅本季度收入、毛利率和现金流风险。"


if __name__ == "__main__":
    # 离线演示入口：不访问真实财务系统，也不需要模型 key。
    state = ksadk_prepare_state({"input": DEMO_QUESTION}, {})
    result = root_agent.invoke(state)
    print(result["answer"])
