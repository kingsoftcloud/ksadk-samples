# 编码 Agent（Workspace + Sandbox）- DeepAgents

用 DeepAgents 工具写法演示 Coding Agent 如何读取 Workspace 文件、规划 Sandbox 命令、生成补丁计划并汇总验证结果。这是一个多文件 DeepAgents Agent 工程，不是单文件脚本；默认离线 demo 不需要模型 key，也不会执行宿主机命令。

## 适用场景

- 想学习 DeepAgents 如何组织长任务编码修复。
- 想对比 DeepAgents、ADK、LangGraph 三种框架写同一 Coding Agent 场景。
- 想把 fixture 替换为真实工作区文件和沙箱执行结果。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | DeepAgents `root_agent` 入口，绑定模型、系统提示词和工具。 |
| `tools.py` | `@tool` Workspace 文件和 Sandbox 命令工具，以及离线渲染。 |
| `data.py` | 本地公开 fixture。 |
| `prompts.py` | 工程修复助手角色和安全边界。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |

## 你会看到什么

- `工作区文件`：Agent 先列出要看的文件和发现。
- `沙箱命令`：Agent 规划隔离环境中的测试命令。
- `补丁计划`：Agent 生成最小修复范围。
- `验证结果`：未连接真实 Sandbox 时明确标注为模拟待执行。

## 环境准备

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

真实模型调用需要 `.env`：

```bash
OPENAI_API_KEY=your-openai-compatible-api-key
OPENAI_MODEL_NAME=gpt-4o-mini
```

## 本地运行

```bash
cd 02-use-cases/coding-agent/workspace-sandbox-deepagents
cp ../../../.env.example .env
uv pip install -r requirements.txt
uv run agentengine run -i .
```

快速看离线输出：

```bash
uv run python demo.py
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以观察 DeepAgents 如何围绕 Workspace / Sandbox 工具组织编码修复。未配置模型时，建议先用 `demo.py` 验证输出结构。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认 Workspace 和 Sandbox 能力已按目标环境配置。

## 示例问题

- `修复 Markdown 表格渲染不稳定的问题，并给出测试计划。`
- `请帮我规划一个 repair_markdown 的补丁和验证命令。`

## 接入真实能力

- Workspace：把 `list_workspace_files` 替换为真实文件 list/read/search。
- Sandbox：把 `plan_sandbox_commands` 替换为真实命令执行和结果采集。
- 补丁：让模型基于文件内容生成 diff，并由用户确认后写入 Workspace。
- CI：把真实执行结果写入 `验证结果`。

## 常见问题

- 如果运行时报 `deepagents` 缺失，请确认已安装 `ksadk[deepagents]` 或 `ksadk[all]`。
- 如果没有模型 key，请先运行 `uv run python demo.py`。
- 如果没有 Sandbox，样例不会执行命令，只展示规划。
- 如果要写文件，请通过 Workspace，不要直接访问任意宿主机目录。
