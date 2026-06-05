from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagents import create_deep_agent
from langchain_core.tools import tool

from common.model_config import make_langchain_chat_model


@tool
def calculate(expression: str) -> dict:
    """计算简单数学表达式。"""

    try:
        return {"status": "success", "result": eval(expression, {"__builtins__": {}}, {})}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@tool
def get_weather(city: str) -> dict:
    """查询示例天气数据。"""

    data = {"北京": "晴，25°C", "上海": "多云，28°C", "深圳": "阵雨，30°C", "广州": "雷阵雨，31°C"}
    return {"city": city, "weather": data.get(city, "暂无示例天气数据")}


root_agent = create_deep_agent(
    model=make_langchain_chat_model(),
    tools=[calculate, get_weather],
    system_prompt="你是 DeepAgents 工具调用示例助手。需要时调用工具，用中文回答。",
)
