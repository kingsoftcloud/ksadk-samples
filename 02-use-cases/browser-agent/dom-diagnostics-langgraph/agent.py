from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from workflow import build_agent_graph, prepare_state


# KSADK 会调用这个函数，把用户请求转换为 LangGraph 状态。
ksadk_prepare_state = prepare_state

# root_agent 是 agentengine.yaml 中声明的入口变量。
root_agent = build_agent_graph()
