# 深度研究报告生成 Agent - LangGraph

把 Deep Research 的证据卡片进一步组织成报告大纲、引用材料、质量检查和最终报告。这是一个多文件 LangGraph Agent 工程，不是单文件脚本；默认使用本地公开示例材料，所以 clone 后不配置模型也能看到完整报告生成流程。

## 适用场景

- 想学习如何把 Deep Research Agent 从“检索答案”升级为“报告交付”。
- 想演示 Web Search / Knowledge Base / Workspace 文档如何进入报告生成链路。
- 想给客户展示一份可复现、可替换真实材料的研究报告 demo。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | KSADK 入口，只暴露 `ksadk_prepare_state` 和 `root_agent`。 |
| `workflow.py` | 装配 LangGraph 节点和报告生成配置。 |
| `tools.py` | 负责材料检索、报告大纲、质量检查和 Markdown 渲染。 |
| `data.py` | 本地公开示例材料，可替换为 Web Search、Knowledge Base 或 Workspace 文件。 |
| `prompts.py` | 报告主笔角色和输出约束。 |
| `demo.py` | 离线演示脚本，一条命令打印完整报告。 |

## 你会看到什么

- `报告大纲`：先确定交付结构。
- `引用材料`：每条结论都带本地材料来源。
- `质量检查`：指出当前证据的不足，避免伪造外部结果。
- `最终报告`：输出一份可直接在 Web UI 中展示的 Markdown 报告。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

这个样例默认不需要模型 key；如果要让真实 LLM 改写报告，可以在 `.env` 中配置：

```bash
OPENAI_API_KEY=your-openai-compatible-api-key
OPENAI_MODEL_NAME=gpt-4o-mini
```

## 本地运行

```bash
cd 02-use-cases/deep-research/report-writer-langgraph
cp ../../../.env.example .env
uv pip install -r requirements.txt
uv run agentengine run -i .
```

如果只想快速看报告输出：

```bash
uv run python demo.py
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以观察问题如何进入 LangGraph，并看到报告大纲、引用材料、质量检查和最终报告。这个样例适合录制“研究报告自动生成”的客户演示。

## 部署

```bash
uv run agentengine deploy .
```

部署前建议先跑 `uv run python demo.py` 和 `uv run agentengine web .`，确认报告结构稳定。

## 示例问题

- `生成一份 Agent Runtime Platform 选型报告。`
- `帮我写一份 KsADK 样例仓库运营建议报告。`

## 接入真实能力

- 接 Web Search：把 `tools.py` 中的 `_score` 和 `collect_evidence` 替换为搜索工具调用。
- 接 Knowledge Base：把 `data.py` 的 `REPORT_SOURCES` 替换为知识库检索结果。
- 接 Workspace：把用户上传的文档解析成 `title`、`quote`、`section`、`quality` 四个字段。
- 接真实 LLM：保留结构化材料，最后在 `render_answer` 阶段调用模型润色报告。

## 常见问题

- 如果运行时报 `langgraph` 缺失，请确认已安装 `ksadk[langgraph]` 或 `ksadk[all]`。
- 如果想接入真实模型，请在 `.env` 中设置 `OPENAI_API_KEY`、`OPENAI_MODEL_NAME`，必要时设置 `OPENAI_BASE_URL`。
- 如果报告看起来像固定模板，这是因为默认离线模式只使用本地 fixture；接入真实搜索或知识库后会随材料变化。
- 如果要展示给客户，建议用 Web UI 输入示例问题并截图最终报告区域。
