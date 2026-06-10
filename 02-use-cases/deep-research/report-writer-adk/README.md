# 深度研究报告生成 Agent - ADK

用 ADK 的工具函数写法实现研究报告生成：Agent 通过 `collect_report_sources` 获取引用材料，再按大纲、质量检查和最终报告组织输出。这是一个多文件 ADK Agent 工程，不是单文件脚本；默认离线 demo 不需要模型 key。

## 适用场景

- 想对比 ADK 和 LangGraph 在报告生成场景里的工程差异。
- 想把 Web Search、Knowledge Base 或 Workspace 文档包装成 ADK 工具。
- 想保留离线可运行 demo，同时为真实 LLM 调用预留工具接口。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | ADK `root_agent` 入口，绑定模型、instruction 和工具函数。 |
| `tools.py` | 报告材料工具和离线 Markdown 渲染。 |
| `data.py` | 本地公开示例材料，可替换为真实检索结果。 |
| `prompts.py` | 报告主笔角色和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |

## 你会看到什么

- `报告大纲`：报告结构先行。
- `引用材料`：所有材料来自本地 fixture。
- `质量检查`：指出证据限制。
- `最终报告`：展示 ADK 工具函数如何支撑报告写作。

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
cd 02-use-cases/deep-research/report-writer-adk
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

Web UI 中可以观察 ADK Agent 如何围绕工具函数组织报告。未配置模型时，建议先用 `demo.py` 验证输出结构。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认模型环境变量和可选知识库配置已就绪。

## 示例问题

- `生成一份 Agent Runtime Platform 选型报告。`
- `帮我写一份 KsADK 样例仓库运营建议报告。`

## 接入真实能力

- Web Search：把 `collect_report_sources` 改成搜索工具封装。
- Knowledge Base：把 `REPORT_SOURCES` 替换为知识库返回结果。
- Workspace：读取用户上传文档后映射为 `title`、`quote`、`section`、`quality`。
- LLM：让 ADK Agent 调用工具后生成自然语言报告。

## 常见问题

- 如果运行时报 `google.adk` 缺失，请确认已安装 `ksadk[adk]` 或 `ksadk[all]`。
- 如果没有模型 key，请先运行 `uv run python demo.py`。
- 如果要保证报告事实可靠，请不要让模型脱离引用材料发挥。
- 如果要开源，请确认 fixture 不包含客户数据或内部地址。
