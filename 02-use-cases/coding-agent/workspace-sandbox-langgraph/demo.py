from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import ksadk_prepare_state, root_agent


DEMO_QUESTION = '修复 Markdown 表格渲染不稳定的问题，并给出测试计划。'


if __name__ == "__main__":
    # 离线演示入口：使用本地 fixture 模拟 Workspace 和 Sandbox，不访问宿主机项目。
    state = ksadk_prepare_state({"input": DEMO_QUESTION}, {})
    result = root_agent.invoke(state)
    print(result["answer"])
