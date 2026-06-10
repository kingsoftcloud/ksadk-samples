# 销售运营 Pipeline Agent - ADK

演示销售运营 Agent 如何把线索、阶段、价值、跟进记录和成交风险组织成下周 pipeline 行动计划。默认使用公开 fixture，不访问真实 CRM。 这是一个多文件 ADK Agent 工程，不是单文件脚本；默认不依赖外部账号，适合作为开源样例和二次开发模板。

## 适用场景

- 想学习 ADK 如何实现 Sales Operations Pipeline Copilot。
- 想把本地 fixture 替换为真实业务系统，同时保留 KSADK 的统一运行和 Web UI 调试体验。
- 想比较 LangGraph / ADK / LangChain / DeepAgents 在同一场景下的工程写法。
- 想为团队沉淀可运行、可部署、可公开审查的 Agent demo。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | ADK `root_agent` 入口。 |
| `tools.py` | 场景工具函数和 Markdown 输出。 |
| `data.py` | 本地公开 fixture，可替换为真实系统。 |
| `prompts.py` | Agent 角色、目标和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |
| `agentengine.yaml` | AgentEngine / KSADK 运行配置。 |

## 你会看到什么

- `线索画像`：先说明输入、目标和约束。
- `跟进策略`：把线索转成可执行路径。
- `CRM 动作`：给出可落地的系统动作。
- `成交风险`：列出发布或成交前必须检查的风险。

## 环境准备

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

单独运行当前样例：

```bash
cd 02-use-cases/sales-operations/pipeline-copilot-adk
cp ../../../.env.example .env
uv pip install -r requirements.txt
```

真实模型调用需要在 `.env` 中配置：

```bash
OPENAI_API_KEY=your-openai-compatible-api-key
OPENAI_MODEL_NAME=gpt-4o-mini
```

## 本地运行

快速看离线输出：

```bash
uv run python demo.py
```

启动 OpenAI-compatible API：

```bash
uv run agentengine run -p 18080 .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以观察 Agent 如何输出 `线索画像`、`跟进策略`、`CRM 动作` 和 `成交风险`。未接入真实系统时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认真实数据源、脱敏规则、审核流程和回滚策略已经配置；未配置时样例只分析本地 fixture。

## 示例问题

- `分析一组销售线索，给出下周跟进计划。`
- `基于当前样例数据，给我一份可执行的下周计划。`

## 接入真实能力

- 把 `LEADS` 替换为 CRM 线索、商机和活动记录。
- 把 `PLAYBOOK` 接入销售方法论、行业话术和客户成功案例。
- 把 `CRM_ACTIONS` 写回 CRM、任务系统或销售周报。
- 接入真实能力后建议继续保留 `demo.py`，用公开 fixture 做回归测试。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或当前框架依赖。
- 如果没有真实业务系统，样例不会访问外部服务，只展示公开 fixture 的完整流程。
- 如果 `agentengine run` 能启动但对话内容为空，请先运行 `uv run python demo.py` 验证工程输出，再检查模型 key、模型网关日志和当前框架 runner 日志。
- 如果要开源，请确认输入数据、输出示例和环境变量不包含真实客户、账号、内部域名或敏感流程。
- 如果要对比其他框架，请切换到同目录下同名场景的 ADK / LangChain / DeepAgents 版本。
