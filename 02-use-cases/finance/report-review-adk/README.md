# 财务报表审阅 Agent - ADK

演示 Finance Agent 如何把报表摘录、风险指标、异常解释和审阅结论组织成可追溯财务分析。这是一个多文件 ADK Agent 工程，不是单文件脚本；默认使用本地公开 fixture，所以 clone 后不配置财务系统也能看到完整审阅流程。

## 适用场景

- 想学习财务分析 Agent 如何把报表数据转成风险判断。
- 想演示收入增长、毛利率下滑、现金流弱化和应收账款变慢的审阅路径。
- 想把 fixture 替换为 Workspace Excel、财务系统 API 或审计数据集。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | ADK `root_agent` 入口。 |
| `tools.py` | 报表读取、风险指标、异常解释和 Markdown 渲染。 |
| `data.py` | 本地公开财务 fixture，可替换为真实报表数据。 |
| `prompts.py` | 财务分析师角色和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |


## 你会看到什么

- `报表摘录`：季度收入、毛利率、经营现金流和应收账款天数。
- `风险指标`：阈值规则、趋势指标和风险判断。
- `异常解释`：收入、毛利率、现金流和应收的解释链路。
- `审阅结论`：需要进一步复核的业务动作。

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
cd 02-use-cases/finance/report-review-adk
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

Web UI 中可以观察 Agent 如何输出报表摘录、风险指标、异常解释和审阅结论。未接入真实财务系统时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认财务数据授权、脱敏规则、审计边界和外部系统凭证已经配置；未配置时样例只分析本地 fixture。

## 示例问题

- `审阅本季度收入、毛利率和现金流风险。`
- `帮我判断 Q3 收入增长背后有没有回款和毛利风险。`

## 接入真实能力

- Workspace Excel：把 `load_financial_report` 替换为用户上传表格解析。
- 财务系统 API：把本地报表 fixture 替换为授权接口数据。
- 审计规则：把 `RISK_THRESHOLDS` 替换为企业风控或审计预审规则。
- 图表产物：把收入、毛利率、现金流趋势输出为 Workspace artifact。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或当前框架 extra。
- 如果没有真实财务系统，样例不会访问外部服务，只展示公开 fixture 的审阅流程。
- 如果风险阈值和你的企业不同，请先修改 `RISK_THRESHOLDS`。
- 如果要开源，请确认报表、客户、合同、回款和审计信息都已脱敏。
