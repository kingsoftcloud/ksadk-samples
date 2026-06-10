# AIOps 告警分诊 Agent - ADK

演示 AIOps Agent 如何把指标告警、日志线索、变更事件和 runbook 组织成 incident triage。这是一个多文件 ADK Agent 工程，不是单文件脚本；默认使用本地公开 fixture，所以 clone 后不配置监控系统也能看到完整分诊流程。

## 适用场景

- 想学习 AIOps Agent 如何把告警和日志转成可执行处置动作。
- 想演示支付链路 5xx、延迟和成功率下降的分诊路径。
- 想把 fixture 替换为 Prometheus、日志平台、Tracing 或变更系统。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | ADK `root_agent` 入口。 |
| `tools.py` | 告警收集、根因线索、runbook 动作和 Markdown 渲染。 |
| `data.py` | 本地公开 AIOps fixture，可替换为真实监控数据。 |
| `prompts.py` | AIOps 值班工程师角色和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |


## 你会看到什么

- `告警摘要`：指标、当前值、基线、窗口和等级。
- `根因线索`：日志线索和变更事件放在同一条判断链路里。
- `处置动作`：可执行 runbook 步骤。
- `复盘事项`：容量、SLO、回滚和告警治理建议。

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
cd 02-use-cases/aiops/incident-triage-adk
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

Web UI 中可以观察 Agent 如何输出告警摘要、根因线索、处置动作和复盘事项。未接入真实监控系统时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认监控、日志、Tracing、变更系统和脱敏规则已经配置；未配置时样例只分析本地 fixture。

## 示例问题

- `分析支付服务 5xx 激增和延迟升高的告警。`
- `帮我判断支付链路是否需要回滚最近一次发布。`

## 接入真实能力

- Prometheus：把 `collect_incident_signals` 替换为指标查询。
- 日志平台：把 `LOG_CLUES` 替换为错误聚合和慢请求样本。
- Tracing：把下游耗时和调用链异常写入根因线索。
- 变更系统：把发布事件和配置变更接入 incident timeline。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或当前框架 extra。
- 如果没有真实监控系统，样例不会访问外部服务，只展示公开 fixture 的分诊流程。
- 如果 runbook 和你的团队不同，请先修改 `RUNBOOK_STEPS` 和 `POSTMORTEM_ITEMS`。
- 如果要开源，请确认日志、指标和变更记录不包含真实客户、账号、内部域名或敏感故障。
