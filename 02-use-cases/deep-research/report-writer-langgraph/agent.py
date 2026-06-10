from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from workflow import build_agent_graph, prepare_state


# KSADK 会读取这个函数，把 AgentEngine 请求 payload 转成 LangGraph 初始状态。
ksadk_prepare_state = prepare_state

# root_agent 是 agentengine.yaml 中声明的入口变量，Web UI 和 run 命令都会加载它。
root_agent = build_agent_graph()
