from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.adk import Agent

from common.model_config import make_adk_litellm_model


def calculate(expression: str) -> dict:
    """计算简单数学表达式。"""

    allowed = {"abs": abs, "round": round, "min": min, "max": max, "sum": sum, "pow": pow}
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)
        return {"status": "success", "expression": expression, "result": result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def get_weather(city: str) -> dict:
    """查询示例天气数据。"""

    data = {
        "北京": "晴，25°C",
        "上海": "多云，28°C",
        "深圳": "阵雨，30°C",
        "广州": "雷阵雨，31°C",
    }
    return {"city": city, "weather": data.get(city, "暂无示例天气数据")}


root_agent = Agent(
    name="tool_calling_adk",
    model=make_adk_litellm_model(),
    description="ADK 工具调用示例。",
    instruction="你是工具调用示例助手。需要计算或查询天气时必须调用工具，再用中文回答。",
    tools=[calculate, get_weather],
)

