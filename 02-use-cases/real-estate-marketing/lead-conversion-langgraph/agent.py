from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from workflow import build_agent_graph, prepare_state


ksadk_prepare_state = prepare_state
root_agent = build_agent_graph()
