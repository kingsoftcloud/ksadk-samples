from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import ksadk_prepare_state, root_agent


DEMO_QUESTION = "分析 Agent 调试功能的激活率和留存变化。"


if __name__ == "__main__":
    # 离线演示入口：不读取真实 CSV，也不会访问外部数据源。
    state = ksadk_prepare_state({"input": DEMO_QUESTION}, {})
    result = root_agent.invoke(state)
    print(result["answer"])
