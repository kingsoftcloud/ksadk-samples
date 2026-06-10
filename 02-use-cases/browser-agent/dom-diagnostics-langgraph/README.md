# 浏览器 Agent（DOM 诊断）- LangGraph

演示 Browser Agent 如何根据页面观察、DOM 线索、失败诊断和验证步骤排查 Web UI 交互问题。这是一个多文件 LangGraph Agent 工程，不是单文件脚本；默认使用本地公开 fixture，所以 clone 后不配置浏览器工具也能看到完整诊断流程。

## 适用场景

- 想学习浏览器 Agent 如何把页面观察变成可执行诊断。
- 想演示 Web UI 首屏、输入框、发送按钮和 Workspace 入口的检查路径。
- 想把 fixture 替换为真实 Playwright / Browser Use / hosted UI 快照。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | LangGraph `root_agent` 入口。 |
| `tools.py` | 页面观察、DOM 线索和验证步骤渲染。 |
| `data.py` | 本地公开 DOM fixture，可替换为真实浏览器快照。 |
| `prompts.py` | 浏览器诊断助手角色和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |
| `workflow.py` | LangGraph 节点编排。 |

## 你会看到什么

- `页面观察`：列出关键控件和状态。
- `DOM 线索`：用 selector 表格说明定位依据。
- `失败诊断`：给出从 bootstrap 到点击无响应的排障顺序。
- `验证步骤`：给出可交给 Playwright 执行的检查流程。

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
cd 02-use-cases/browser-agent/dom-diagnostics-langgraph
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

Web UI 中可以观察 Agent 如何输出页面观察、DOM 线索、失败诊断和验证步骤。未接入真实浏览器工具时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认目标环境是否需要真实浏览器执行能力；未配置时样例只做诊断规划。

## 示例问题

- `验证本地 Web UI 首页无法点击发送按钮的问题。`
- `帮我检查 Web UI 输入框和发送按钮为什么没有响应。`

## 接入真实能力

- Playwright：把 `collect_page_observations` 替换为页面 snapshot 和 selector 检查。
- Browser Use：把观察结果映射为 `selector`、`role`、`state`、`finding`。
- Web UI 日志：把后端 `/agentengine/api/v1` 请求状态写入失败诊断。
- 截图：把关键步骤截图保存到 `assets/screenshots/` 后在 README 引用。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或当前框架 extra。
- 如果没有浏览器工具，样例不会真的打开网页，只展示诊断流程。
- 如果要录制真实演示，请先启动 `agentengine web`，再用 Playwright 录制输入和回答。
- 如果要开源，请确认截图不包含账号、token 或内部地址。
