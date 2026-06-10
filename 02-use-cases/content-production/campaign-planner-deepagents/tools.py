from __future__ import annotations

from data import CAMPAIGN_BRIEF, CHANNELS, DRAFTS, REVIEW_ITEMS
from prompts import SYSTEM_PROMPT, TITLE


def load_campaign_brief(query: str) -> dict:
    """读取传播 brief。

    真实项目里这里可以替换为产品发布计划、GitHub Release 或 CMS brief。
    """

    return CAMPAIGN_BRIEF


def plan_channels(query: str) -> list[dict]:
    """生成渠道计划。"""

    return CHANNELS


def draft_content(query: str) -> list[dict]:
    """生成内容草稿。"""

    return DRAFTS


def _render_brief() -> str:
    audience = "、".join(CAMPAIGN_BRIEF["audience"])
    return (
        f"- 产品：{CAMPAIGN_BRIEF['product']}\n"
        f"- 目标受众：{audience}\n"
        f"- 传播目标：{CAMPAIGN_BRIEF['objective']}\n"
        f"- 语气：{CAMPAIGN_BRIEF['tone']}"
    )


def _render_channels() -> str:
    lines = ["| 渠道 | 目的 | 资产 |", "| --- | --- | --- |"]
    for item in CHANNELS:
        lines.append(f"| {item['name']} | {item['purpose']} | {item['asset']} |")
    return "\n".join(lines)


def _render_drafts() -> str:
    return "\n".join(f"- **{item['format']}**：{item['text']}" for item in DRAFTS)


def _render_reviews() -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(REVIEW_ITEMS, 1))


def render_demo_answer(query: str) -> str:
    """生成离线内容传播计划。"""

    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地公开 fixture，适合替换为真实发布 brief、CMS 和审核流程。

## 创意简报

{_render_brief()}

## 渠道计划

{_render_channels()}

## 内容草稿

{_render_drafts()}

## 审核清单

{_render_reviews()}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责读取 brief、规划渠道、生成草稿和审核清单。
- `data.py` 可替换为真实发布计划、CMS、社媒排期或品牌审核系统。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    brief = load_campaign_brief(query)
    return [brief] + plan_channels(query) + draft_content(query)


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": "内容策略负责人", "action": item, "why": "发布前事实核查和品牌一致性。"}
        for index, item in enumerate(REVIEW_ITEMS, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
