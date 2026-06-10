from __future__ import annotations

from data import PATCH_PLAN, SANDBOX_COMMANDS, WORKSPACE_FILES
from prompts import ROLE, SYSTEM_PROMPT, TITLE


def _score(query: str, item: dict) -> int:
    """对模拟 Workspace 文件做关键词匹配。

    真实项目里这里应该替换为 Workspace list/read/search 工具调用，而不是直接读宿主机目录。
    """

    text = f"{item['path']} {item['purpose']} {item['finding']}".lower()
    tokens = [part for part in query.lower().replace('，', ' ').replace('。', ' ').split() if part]
    return sum(text.count(token) for token in tokens) or int(any(ch in text for ch in query[:10]))


def collect_evidence(query: str) -> list[dict]:
    """收集模拟工作区文件证据。"""

    ranked = sorted(WORKSPACE_FILES, key=lambda item: (_score(query, item), item['path']), reverse=True)
    return [
        {
            'id': item['path'],
            'title': item['path'],
            'summary': item['finding'],
            'purpose': item['purpose'],
            'source': 'local-workspace-fixture',
        }
        for item in ranked
    ]


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """把文件证据转成修复行动。"""

    actions = []
    for index, plan in enumerate(PATCH_PLAN, 1):
        evidence_title = evidence[(index - 1) % len(evidence)]['title'] if evidence else '模拟工作区'
        actions.append(
            {
                'step': index,
                'owner': ROLE,
                'action': plan,
                'why': f"参考 `{evidence_title}` 的发现。",
            }
        )
    return actions


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """渲染 Coding Agent 的修复闭环。"""

    workspace_lines = '\n'.join(
        f"- `{item['title']}`：{item['purpose']}；发现：{item['summary']}（来源：{item['source']}）"
        for item in evidence
    ) or '- 暂无工作区文件。'
    command_lines = '\n'.join(
        f"| `{command}` | {purpose} | 模拟待执行 |"
        for command, purpose in SANDBOX_COMMANDS
    )
    patch_lines = '\n'.join(
        f"{item['step']}. **{item['action']}** - {item['why']}"
        for item in actions
    ) or '1. 补充工作区文件后重新规划。'
    result_lines = '\n'.join(
        f"- {purpose}：当前 demo 未连接真实 Sandbox，建议接入后执行 `{command}` 并记录 exit code。"
        for command, purpose in SANDBOX_COMMANDS
    )
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith('这个场景')), '')
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line or '这个 demo 已完成一次编码修复规划。'} 当前输出使用本地 fixture 模拟 Workspace 和 Sandbox，适合替换为真实平台工具后演示代码修复闭环。

## 工作区文件

{workspace_lines}

## 沙箱命令

| 命令 | 用途 | 状态 |
| --- | --- | --- |
{command_lines}

## 补丁计划

{patch_lines}

## 验证结果

{result_lines}

## 行动计划

{patch_lines}

## 工程说明

- `agent.py` 只负责暴露 KSADK 入口。
- `workflow.py` 负责 LangGraph 编排。
- `tools.py` 负责模拟 Workspace 文件、Sandbox 命令和补丁计划。
- `data.py` 和 `prompts.py` 存放可替换的文件证据、命令清单和安全约束。
""".strip()


def render_demo_answer(query: str) -> str:
    """供 demo.py、测试和其他框架版本复用的离线编码修复入口。"""

    evidence = collect_evidence(query)
    actions = plan_actions(query, evidence)
    return render_answer(query, evidence, actions)
