# 客服 Agent（工单分级）- ADK

演示 Customer Support Agent 如何把客户问题转成工单摘要、知识匹配、处理步骤和升级策略。这是一个多文件 ADK Agent 工程，不是单文件脚本；默认使用本地公开 fixture，所以 clone 后不配置客服系统也能看到完整处理流程。

## 适用场景

- 想学习客服 Agent 如何做工单分级和知识匹配。
- 想演示 Web UI 无响应、Skill 未调用、Markdown 渲染异常等常见问题的处理路径。
- 想把 fixture 替换为 KSADK Knowledge Base、工单系统或企业客服 API。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | ADK `root_agent` 入口。 |
| `tools.py` | 知识检索、工单分级、处理步骤和升级策略渲染。 |
| `data.py` | 本地公开客服知识 fixture，可替换为真实知识库。 |
| `prompts.py` | 客户支持专家角色和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |


## 你会看到什么

- `工单摘要`：标题、严重等级、影响判断和命中知识。
- `知识匹配`：列出匹配条目、症状和处理建议。
- `处理步骤`：给客户可执行的排障动作。
- `升级策略`：根据等级给出升级对象和触发条件。

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
cd 02-use-cases/customer-support/ticket-triage-adk
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

Web UI 中可以观察 Agent 如何输出工单摘要、知识匹配、处理步骤和升级策略。未接入真实客服系统时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认知识库、工单系统和客户数据脱敏策略已经配置；未配置时样例只分析本地 fixture。

## 示例问题

- `客户说 Web UI 启动后没有响应，帮我排查。`
- `客户问 Skill Space 配好了但工具没调用，怎么回复？`

## 接入真实能力

- Knowledge Base：把 `search_support_knowledge` 替换为知识库检索。
- 工单系统：把 `classify_ticket` 的结果写入企业工单 API。
- Workspace：把客户日志保存为会话文件，方便研发复现。
- Tracing：把每次知识匹配和升级决策写入 OpenTelemetry trace。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或当前框架 extra。
- 如果没有真实客服系统，样例不会访问外部服务，只展示公开 fixture 的处理流程。
- 如果严重等级不符合你的团队规则，请先修改 `ESCALATION_POLICY`。
- 如果要开源，请确认知识条目不包含真实客户、账号、token 或内部故障详情。
