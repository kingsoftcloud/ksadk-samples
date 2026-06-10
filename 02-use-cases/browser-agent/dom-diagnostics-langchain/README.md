# 浏览器 Agent（DOM 诊断）- LangChain

演示 LangChain Agent 如何把页面观察、DOM 线索、失败诊断和验证步骤组织成浏览器排障流程。 这是一个多文件 LangChain Agent 工程，不是单文件脚本；默认使用本地公开 fixture，所以 clone 后不配置外部服务也能看到完整流程。

## 适用场景

- 想学习同一业务场景在 LangChain 中如何组织 `create_agent` 和工具函数。
- 想对比 LangGraph / ADK / LangChain / DeepAgents 的入口差异，而不是只看单框架写法。
- 想把本地 fixture 替换为真实模型、Workspace、Sandbox、Knowledge Base 或业务 API。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | LangChain `root_agent` 入口，使用 `create_agent` 绑定工具。 |
| `tools.py` | 场景工具和离线 Markdown 渲染。 |
| `data.py` | 本地公开 fixture，可替换为真实数据源或平台能力。 |
| `prompts.py` | 角色设定和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |

## 你会看到什么

- `页面观察`：查看 页面观察 阶段的结构化输出。
- `DOM 线索`：查看 DOM 线索 阶段的结构化输出。
- `失败诊断`：查看 失败诊断 阶段的结构化输出。
- `验证步骤`：查看 验证步骤 阶段的结构化输出。

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
cd 02-use-cases/browser-agent/dom-diagnostics-langchain
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

Web UI 中可以观察 LangChain Agent 如何绑定工具并输出结构化 Markdown。未接入真实平台能力时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认真实数据源、外部服务凭证、网络策略和脱敏规则已经配置；未配置时样例只使用本地 fixture。

## 示例问题

- `验证本地 Web UI 首页无法点击发送按钮的问题。`
- `请用 LangChain 版本演示一次完整流程。`

## 接入真实能力

- Playwright：把 `collect_page_observations` 替换为真实 snapshot。
- Browser Use：把浏览器观察映射为 selector、role 和 state。
- 截图：把关键步骤保存到 assets/screenshots 并在 README 引用。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或 `ksadk[langchain]`。
- 如果没有模型 key，可以先运行 `uv run python demo.py` 查看离线输出。
- 如果要接入真实平台能力，请先替换 `tools.py`，再更新 README 中的验证步骤。
- 如果要开源，请确认 fixture、日志和截图不包含真实账号、token、内部域名或客户数据。
