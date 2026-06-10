from __future__ import annotations

from data import ACTION_TEMPLATES, RESEARCH_STAGES, SCENARIO_EVIDENCE
from prompts import ROLE, SYSTEM_PROMPT, TITLE


def _score(query: str, item: dict) -> int:
    """对本地证据做一个透明的关键词打分。

    样例故意不用外部向量库，保证用户 clone 后不配置云资源也能运行。
    如果要接 KSADK Knowledge Base，可以把这个函数替换成 search_knowledge 调用。
    """

    text = f"{item['title']} {item['content']}".lower()
    tokens = [part for part in query.lower().replace('，', ' ').replace('。', ' ').split() if part]
    return sum(text.count(token) for token in tokens) or int(any(ch in text for ch in query[:12]))


def collect_evidence(query: str) -> list[dict]:
    """检索场景证据卡片。"""

    ranked = sorted(
        SCENARIO_EVIDENCE,
        key=lambda item: (_score(query, item), item['id']),
        reverse=True,
    )
    selected = ranked[:3]
    return [
        {
            'id': item['id'],
            'title': item['title'],
            'summary': item['content'],
            'angle': item['angle'],
            'gap': item['gap'],
            'source': 'local-demo-data',
        }
        for item in selected
    ]


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """把证据转成可执行计划。"""

    actions = []
    for index, template in enumerate(ACTION_TEMPLATES, 1):
        evidence_title = evidence[(index - 1) % len(evidence)]['title'] if evidence else '本地示例数据'
        actions.append(
            {
                'step': index,
                'owner': ROLE,
                'action': template,
                'why': f"基于证据《{evidence_title}》推进。",
            }
        )
    return actions


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """渲染 Web UI 友好的 Markdown 回答。"""

    plan_lines = '\n'.join(f"{index}. {stage}" for index, stage in enumerate(RESEARCH_STAGES, 1))
    trace_lines = '\n'.join(
        f"- `{item['id']}`：围绕 **{item['angle']}** 检索到《{item['title']}》。"
        for item in evidence
    ) or '- 暂无执行轨迹。'
    evidence_lines = '\n'.join(
        f"- **{item['title']}**：{item['summary']}（角度：{item['angle']}；来源：{item['source']}）"
        for item in evidence
    ) or '- 暂无证据。'
    reflection_lines = '\n'.join(
        f"- **{item['angle']}**：{item['gap']}"
        for item in evidence
    ) or '- 需要补充更多证据后再反思。'
    action_lines = '\n'.join(
        f"{item['step']}. **{item['action']}** - {item['why']}"
        for item in actions
    ) or '1. 补充输入后重新规划。'
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith('这个场景')), '')
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line or '这个 demo 已完成一次可复现推理。'} 这个 demo 已用本地数据完成一次可复现推理，适合直接在 `agentengine web` 中演示。

## 研究计划

{plan_lines}

## 执行轨迹

{trace_lines}

## 证据卡片

{evidence_lines}

## 反思与补查

{reflection_lines}

## 行动计划

{action_lines}

## 交付物

- 一份含结论、证据、风险和下一步行动的研究简报。
- 一组可继续接入 Knowledge Base / Workspace / Web Search 的替换点。
- 一条可在 Web UI 中复现的 LangGraph 执行链路。

## 工程说明

- `agent.py` 只负责暴露 KSADK 入口。
- `workflow.py` 负责 LangGraph 编排。
- `tools.py` 负责检索、计划和 Markdown 输出。
- `data.py` 和 `prompts.py` 存放可替换的业务数据和提示词。
""".strip()
