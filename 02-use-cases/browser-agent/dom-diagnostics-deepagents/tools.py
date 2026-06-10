from __future__ import annotations

from langchain_core.tools import tool

from data import DIAGNOSTIC_RULES, PAGE_OBSERVATIONS, VERIFY_STEPS
from prompts import SYSTEM_PROMPT, TITLE


@tool
def collect_page_observations(query: str) -> list[dict]:
    """收集页面观察结果。

    这里默认返回本地 fixture，真实项目可替换为 Playwright snapshot 或浏览器工具输出。
    """

    return PAGE_OBSERVATIONS


@tool
def plan_verify_steps(query: str) -> list[str]:
    """规划浏览器验证步骤。"""

    return VERIFY_STEPS


def render_demo_answer(query: str) -> str:
    """生成离线浏览器诊断报告。"""

    observations = PAGE_OBSERVATIONS
    steps = VERIFY_STEPS
    page_lines = "\n".join(
        f"- **{item['role']}**：`{item['selector']}`，状态：{item['state']}；{item['finding']}"
        for item in observations
    )
    dom_lines = "\n".join(
        f"| `{item['selector']}` | {item['role']} | {item['state']} |"
        for item in observations
    )
    diagnosis_lines = "\n".join(f"- {rule}" for rule in DIAGNOSTIC_RULES)
    verify_lines = "\n".join(f"{index}. {step}" for index, step in enumerate(steps, 1))
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith('这个场景')), '')
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地 DOM fixture，不伪造真实浏览器结果；接入 Playwright 后可把观察结果替换为真实页面快照。

## 页面观察

{page_lines}

## DOM 线索

| Selector | 作用 | 状态 |
| --- | --- | --- |
{dom_lines}

## 失败诊断

{diagnosis_lines}

## 验证步骤

{verify_lines}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责页面观察、DOM 线索和验证步骤。
- `data.py` 可替换为真实浏览器快照或 Playwright 输出。
""".strip()
