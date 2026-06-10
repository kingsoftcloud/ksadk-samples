# 数据分析 Agent（CSV 洞察）- LangGraph

演示 Data Analyst Agent 如何把 CSV 样本转成指标口径、洞察排序和图表建议。这是一个多文件 LangGraph Agent 工程，不是单文件脚本；默认使用本地公开 fixture，所以 clone 后不配置数据平台也能看到完整分析流程。

## 适用场景

- 想学习数据分析 Agent 如何把表格数据拆成可解释指标。
- 想演示 Agent 产品运营中的激活率、留存率和 Web UI 使用强度分析。
- 想把 fixture 替换为 Workspace 上传 CSV、DuckDB 查询结果或 BI API。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | LangGraph `root_agent` 入口。 |
| `tools.py` | CSV 加载、指标计算、洞察排序和 Markdown 渲染。 |
| `data.py` | 本地公开 CSV fixture，可替换为真实数据源。 |
| `prompts.py` | 数据分析师角色和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |
| `workflow.py` | LangGraph 编排：加载数据、计算指标、排序洞察、渲染回答。 |

## 你会看到什么

- `数据样本`：展示用于分析的 CSV 行数据。
- `指标口径`：明确每个指标的公式和业务含义。
- `洞察排序`：按变化幅度和行动价值排列结论。
- `图表建议`：给出适合产出到 Web UI 或报告中的图表。

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
cd 02-use-cases/data-analyst/csv-insight-langgraph
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

Web UI 中可以观察 Agent 如何输出数据样本、指标口径、洞察排序和图表建议。未接入真实数据源时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认真实数据源的访问凭证、网络策略和脱敏规则已经配置；未配置时样例只分析本地 fixture。

## 示例问题

- `分析 Agent 调试功能的激活率和留存变化。`
- `帮我基于 CSV 看看 Web UI 使用强度是否提升了留存。`

## 接入真实能力

- Workspace CSV：把用户上传文件解析为 `CSV_ROWS` 的同构列表。
- DuckDB：在 `tools.py` 中用 SQL 聚合周指标，再复用渲染函数。
- BI API：把接口返回结果映射为 `visitors`、`activated`、`retained`、`webui_runs`。
- 图表产物：把 `CHART_SUGGESTIONS` 扩展为 ECharts / Vega-Lite spec，并写入 Workspace artifact。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或当前框架 extra。
- 如果没有真实 CSV，样例不会访问外部数据，只展示公开 fixture 的分析流程。
- 如果指标口径和你的业务不同，请先修改 `METRIC_DEFINITIONS`，再改渲染逻辑。
- 如果要开源，请确认示例数据不包含真实用户、账号、内部域名或敏感业务指标。
