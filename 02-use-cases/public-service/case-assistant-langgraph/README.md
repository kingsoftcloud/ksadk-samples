# 政务服务事项协同 Agent - LangGraph

政务服务 Agent 如何把事项画像、材料核验、协同流程和服务承诺组织成可执行办事方案。默认使用公开虚构数据，不包含真实个人、企业或政务材料。 这是一个多文件 LangGraph Agent 工程，不是单文件脚本；默认不依赖外部账号，适合作为开源样例和二次开发模板。

## 适用场景

- 想学习 LangGraph 如何实现 Public Service Case Assistant Agent。
- 想把本地 fixture 替换为真实业务系统，同时保留 KSADK 的统一运行和 Web UI 调试体验。
- 想比较 LangGraph / ADK / LangChain / DeepAgents 在同一场景下的工程写法。
- 想为团队沉淀可运行、可部署、可公开审查的 Agent demo。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | LangGraph `root_agent` 入口。 |
| `tools.py` | 场景工具函数和 Markdown 输出。 |
| `data.py` | 本地公开 fixture，可替换为真实系统。 |
| `prompts.py` | Agent 角色、目标和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |
| `workflow.py` | LangGraph 编排：证据收集、行动规划、输出报告。 |
| `agentengine.yaml` | AgentEngine / KSADK 运行配置。 |

## 你会看到什么

- `事项画像`：整理事项类型、办理对象、当前状态和高频卡点。
- `材料核验`：检查材料完整性、缺失项和可线上补正项。
- `协同流程`：生成窗口、后台审批、短信提醒和回访协同动作。
- `服务承诺`：明确时限、透明度、隐私和人工复核边界。

## 环境准备

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

单独运行当前样例：

```bash
cd 02-use-cases/public-service/case-assistant-langgraph
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

Web UI 中可以观察 Agent 如何输出 `事项画像`、`材料核验`、`协同流程` 和 `服务承诺`。未接入真实系统时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认真实数据源、脱敏规则、审核流程和回滚策略已经配置；未配置时样例只分析本地 fixture。

## 示例问题

- `整理一批政务服务事项，生成办事协同方案。`
- `基于当前样例数据，给我一份可执行的行动计划。`

## 接入真实能力

- 把 `CASE_PROFILE` 替换为政务服务平台和办件状态的脱敏数据。
- 把 `MATERIAL_CHECKS` 接入材料库、规则库和补正记录。
- 把协同流程写回办件系统、短信提醒或服务回访看板；审批结论必须人工复核。
- 接入真实能力后建议继续保留 `demo.py`，用公开 fixture 做回归测试。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或当前框架依赖。
- 如果没有真实业务系统，样例不会访问外部服务，只展示公开 fixture 的完整流程。
- 如果 `agentengine run` 能启动但对话内容为空，请先运行 `uv run python demo.py` 验证工程输出，再检查模型 key、模型网关日志和当前框架 runner 日志。
- 如果要开源，请确认输入数据、输出示例和环境变量不包含真实个人信息、真实客户、账号、内部域名或敏感流程。
- 如果要对比其他框架，请切换到同一场景下的 LangGraph / ADK / LangChain / DeepAgents 版本。
