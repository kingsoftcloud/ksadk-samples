# 农业生产农事计划 Agent - LangGraph

农业生产 Agent 如何围绕种植计划、环境数据、农事任务和产量预测生成公开可复现的农事生产计划。默认使用虚构农业 fixture，不包含真实地块、真实农户、真实产量或商业采购数据。 这是一个多文件 LangGraph Agent 工程，不是单文件脚本；默认不依赖外部账号，适合作为开源样例和二次开发模板。

## 适用场景

- 想学习 LangGraph 如何实现 农业生产农事计划 Agent。
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

- `种植计划`：用公开虚构数据展示种植单元当前状态。
- `环境数据`：把资源、服务或环境数据拆成可核验条目。
- `农事任务`：生成下一步行动，明确哪些需要人工复核。
- `产量预测`：说明合规、安全、经营或产量风险的控制方式。

## 环境准备

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

单独运行当前样例：

```bash
cd 02-use-cases/agriculture-production/crop-planner-langgraph
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

Web UI 中可以观察 Agent 如何输出 `种植计划`、`环境数据`、`农事任务` 和 `产量预测`。未接入真实系统时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认真实数据源、脱敏规则、审核流程和回滚策略已经配置；未配置时样例只分析本地 fixture。

## 示例问题

- `分析一组农业生产数据，生成农事生产计划。`
- `基于当前样例数据，给我一份可执行的行动计划。`

## 接入真实能力

- 把 `CROP_PLAN` 替换为农事计划系统、IoT 传感器、天气服务、农技巡检记录和采收台账中的脱敏摘要。
- 把 `ENVIRONMENT_DATA` 接入真实资源、服务、环境或经营指标，但不要在样例输出中展示敏感字段。
- 把 `FARMING_TASKS` 写回任务系统、运营工作台或复盘文档；关键结论必须保留人工确认。
- 接入真实能力后建议继续保留 `demo.py`，用公开 fixture 做回归测试。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或当前框架依赖。
- 如果没有真实业务系统，样例不会访问外部服务，只展示公开 fixture 的完整流程。
- 如果 `agentengine run` 能启动但对话内容为空，请先运行 `uv run python demo.py` 验证工程输出，再检查模型 key、模型网关日志和当前框架 runner 日志。
- 如果要开源，请确认输入数据、输出示例和环境变量不包含真实个人信息、真实客户、账号、内部域名或敏感流程。
- 如果要对比其他框架，请切换到同一场景下的 LangGraph / ADK / LangChain / DeepAgents 版本。
