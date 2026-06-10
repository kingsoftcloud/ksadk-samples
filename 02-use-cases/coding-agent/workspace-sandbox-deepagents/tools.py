from __future__ import annotations

from langchain_core.tools import tool

from data import PATCH_PLAN, SANDBOX_COMMANDS, WORKSPACE_FILES
from prompts import SYSTEM_PROMPT, TITLE


@tool
def list_workspace_files(query: str) -> list[dict]:
    """列出和问题相关的 Workspace 文件。"""

    return WORKSPACE_FILES


@tool
def plan_sandbox_commands(query: str) -> list[dict]:
    """规划需要在 Sandbox 中执行的命令。"""

    return [{'command': command, 'purpose': purpose, 'status': '模拟待执行'} for command, purpose in SANDBOX_COMMANDS]


def render_demo_answer(query: str) -> str:
    """生成离线编码修复计划。"""

    evidence = WORKSPACE_FILES
    commands = [{'command': command, 'purpose': purpose, 'status': '模拟待执行'} for command, purpose in SANDBOX_COMMANDS]
    workspace_lines = '\n'.join(
        f"- `{item['path']}`：{item['purpose']}；发现：{item['finding']}（来源：local-workspace-fixture）"
        for item in evidence
    )
    command_lines = '\n'.join(f"| `{item['command']}` | {item['purpose']} | {item['status']} |" for item in commands)
    patch_lines = '\n'.join(
        f"{index}. **{plan}** - 参考 `{evidence[(index - 1) % len(evidence)]['path']}` 的发现。"
        for index, plan in enumerate(PATCH_PLAN, 1)
    )
    result_lines = '\n'.join(
        f"- {item['purpose']}：当前 DeepAgents demo 未连接真实 Sandbox，建议接入后执行 `{item['command']}` 并记录 exit code。"
        for item in commands
    )
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith('这个场景')), '')
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} DeepAgents 版本适合扩展成长任务编码修复，但默认仍遵守 Workspace/Sandbox 边界。

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

## 工程说明

- `agent.py` 暴露 DeepAgents `root_agent`。
- `tools.py` 使用 `@tool` 包装 Workspace 和 Sandbox 能力。
- `data.py` 可替换为真实工作区文件和命令输出。
""".strip()
