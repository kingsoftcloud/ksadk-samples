from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import ksadk_prepare_state, root_agent


DEMO_QUESTION = "客户说 Web UI 启动后没有响应，帮我排查。"


if __name__ == "__main__":
    # 离线演示入口：不连接真实客服系统，也不需要模型 key。
    state = ksadk_prepare_state({"input": DEMO_QUESTION}, {})
    result = root_agent.invoke(state)
    print(result["answer"])
