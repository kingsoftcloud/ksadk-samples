# 深度研究报告生成 Agent - LangChain

演示 LangChain Agent 如何把本地证据、报告大纲、质量检查和引用材料组织成研究报告。 这是一个多文件 LangChain Agent 工程，不是单文件脚本；默认使用本地公开 fixture，所以 clone 后不配置外部服务也能看到完整流程。

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

- `报告大纲`：查看 报告大纲 阶段的结构化输出。
- `引用材料`：查看 引用材料 阶段的结构化输出。
- `质量检查`：查看 质量检查 阶段的结构化输出。
- `最终报告`：查看 最终报告 阶段的结构化输出。

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
cd 02-use-cases/deep-research/report-writer-langchain
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

- `生成一份 Agent Runtime Platform 选型报告。`
- `请用 LangChain 版本演示一次完整流程。`

## 接入真实能力

- Web Search：把 `collect_report_sources` 替换为搜索工具。
- Knowledge Base：把本地材料替换为企业知识库检索。
- Workspace：把报告草稿写入会话文件并在 Web UI 下载。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或 `ksadk[langchain]`。
- 如果没有模型 key，可以先运行 `uv run python demo.py` 查看离线输出。
- 如果要接入真实平台能力，请先替换 `tools.py`，再更新 README 中的验证步骤。
- 如果要开源，请确认 fixture、日志和截图不包含真实账号、token、内部域名或客户数据。
