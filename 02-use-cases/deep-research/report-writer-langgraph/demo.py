from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import ksadk_prepare_state, root_agent


DEMO_QUESTION = '生成一份 Agent Runtime Platform 选型报告。'


if __name__ == "__main__":
    # 离线演示入口：不需要模型 key，也不会访问外部搜索服务。
    state = ksadk_prepare_state({"input": DEMO_QUESTION}, {})
    result = root_agent.invoke(state)
    print(result["answer"])
