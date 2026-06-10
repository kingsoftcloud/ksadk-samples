# 多 Agent 团队（协作交付）- LangChain

演示 LangChain Agent 如何把复杂任务拆成角色分工、并行轨迹、冲突合并和验收清单。 这是一个多文件 LangChain Agent 工程，不是单文件脚本；默认使用本地公开 fixture，所以 clone 后不配置外部服务也能看到完整流程。

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

- `角色分工`：查看 角色分工 阶段的结构化输出。
- `并行轨迹`：查看 并行轨迹 阶段的结构化输出。
- `冲突合并`：查看 冲突合并 阶段的结构化输出。
- `验收清单`：查看 验收清单 阶段的结构化输出。

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
cd 02-use-cases/multi-agent-team/team-delivery-langchain
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

- `组织一个团队把 samples 仓库补齐。`
- `请用 LangChain 版本演示一次完整流程。`

## 接入真实能力

- 子 Agent：把角色 fixture 替换为真实 Agent 注册表。
- 任务队列：把并行轨迹替换为队列状态查询。
- Reviewer：把 public-preflight 和 smoke 结果写入验收清单。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或 `ksadk[langchain]`。
- 如果没有模型 key，可以先运行 `uv run python demo.py` 查看离线输出。
- 如果要接入真实平台能力，请先替换 `tools.py`，再更新 README 中的验证步骤。
- 如果要开源，请确认 fixture、日志和截图不包含真实账号、token、内部域名或客户数据。
