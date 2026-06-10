# 编码 Agent（Workspace + Sandbox）- LangGraph

演示 Coding Agent 如何读取 Workspace 文件、规划 Sandbox 命令、生成补丁计划并汇总验证结果。这是一个多文件 LangGraph Agent 工程，不是单文件脚本；默认使用本地公开 fixture 模拟工作区和沙箱，所以 clone 后不配置云资源也能看到完整修复闭环。

## 适用场景

- 想学习 Coding Agent 如何在 KSADK 里遵守 Workspace / Sandbox 边界。
- 想演示“读文件、计划补丁、跑测试、汇总风险”的工程闭环。
- 想把本地 fixture 替换为真实 Workspace 文件和 Sandbox 命令执行。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | KSADK 入口，只暴露 `ksadk_prepare_state` 和 `root_agent`。 |
| `workflow.py` | 装配 LangGraph 节点和场景配置。 |
| `tools.py` | 模拟 Workspace 文件读取、Sandbox 命令规划和验证结果汇总。 |
| `data.py` | 本地公开 fixture，可替换为真实工作区文件和命令结果。 |
| `prompts.py` | 工程修复助手角色和安全边界说明。 |
| `demo.py` | 离线演示脚本，一条命令打印完整修复计划。 |

## 你会看到什么

- `工作区文件`：Agent 先列出要看的文件和发现。
- `沙箱命令`：Agent 规划应该在隔离环境中执行的测试命令。
- `补丁计划`：Agent 生成最小修复范围。
- `验证结果`：未连接真实 Sandbox 时明确标注为模拟待执行，不伪造结果。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

这个样例默认不需要模型 key；如果要让真实 LLM 生成补丁说明，可以在 `.env` 中配置：

```bash
OPENAI_API_KEY=your-openai-compatible-api-key
OPENAI_MODEL_NAME=gpt-4o-mini
```

## 本地运行

```bash
cd 02-use-cases/coding-agent/workspace-sandbox-langgraph
cp ../../../.env.example .env
uv pip install -r requirements.txt
uv run agentengine run -i .
```

如果只想快速看演示效果：

```bash
uv run python demo.py
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以观察 Coding Agent 如何从用户问题生成工作区文件清单、沙箱命令、补丁计划和验证结果。这个样例适合演示“编码修复不能直接碰宿主机，应该通过平台边界执行”。

## 部署

```bash
uv run agentengine deploy .
```

部署前建议确认真实运行环境已配置 Workspace 和 Sandbox；未配置时，样例会保留本地 fixture 行为，不伪造执行结果。

## 示例问题

- `修复 Markdown 表格渲染不稳定的问题，并给出测试计划。`
- `请帮我规划一个 repair_markdown 的补丁和验证命令。`

## 接入真实能力

- 接 Workspace：把 `tools.py` 中的 `collect_evidence` 替换为 Workspace list/read/search 工具调用。
- 接 Sandbox：把 `SANDBOX_COMMANDS` 交给 Sandbox 执行，记录 stdout、stderr 和 exit code。
- 接真实补丁：把 `PATCH_PLAN` 替换为模型生成的 diff，再让用户确认后写入 Workspace。
- 接 CI：把 `make public-preflight` 等命令的真实输出写入 `验证结果`。

## 常见问题

- 如果运行时报 `langgraph` 缺失，请确认已安装 `ksadk[langgraph]` 或 `ksadk[all]`。
- 如果没有配置 Sandbox，样例不会执行命令，只展示建议命令和模拟状态。
- 如果要让 Agent 写文件，请优先接入 Workspace，不要让样例直接修改任意宿主机目录。
- 如果要展示给客户，建议先用 `uv run python demo.py` 确认输出，再用 `agentengine web` 录制交互。
