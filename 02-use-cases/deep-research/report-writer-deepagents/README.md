# 深度研究报告生成 Agent - DeepAgents

用 DeepAgents 的工具写法实现研究报告生成：Agent 通过 `collect_report_sources` 获取引用材料，再输出报告大纲、质量检查和最终报告。这是一个多文件 DeepAgents Agent 工程，不是单文件脚本；默认离线 demo 不需要模型 key。

## 适用场景

- 想学习 DeepAgents 在长任务报告生成里的工程组织。
- 想对比 DeepAgents、ADK、LangGraph 三种框架写同一报告场景的差异。
- 想把搜索、知识库或 Workspace 文档接入 DeepAgents 工具。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | DeepAgents `root_agent` 入口，绑定模型、系统提示词和工具。 |
| `tools.py` | `@tool` 材料检索和离线 Markdown 渲染。 |
| `data.py` | 本地公开示例材料。 |
| `prompts.py` | 报告主笔角色和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |

## 你会看到什么

- `报告大纲`：报告结构先行。
- `引用材料`：所有材料来自本地 fixture。
- `质量检查`：指出证据限制。
- `最终报告`：展示 DeepAgents 工具如何支撑报告写作。

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
cd 02-use-cases/deep-research/report-writer-deepagents
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

Web UI 中可以观察 DeepAgents 如何围绕工具函数组织报告。未配置模型时，建议先用 `demo.py` 验证输出结构。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认模型环境变量和可选知识库配置已就绪。

## 示例问题

- `生成一份 Agent Runtime Platform 选型报告。`
- `帮我写一份 KsADK 样例仓库运营建议报告。`

## 接入真实能力

- Web Search：把 `collect_report_sources` 改成搜索工具。
- Knowledge Base：把 `REPORT_SOURCES` 替换为知识库返回结果。
- Workspace：读取用户上传文档后映射为报告材料。
- LLM：让 DeepAgents 调用工具后生成自然语言报告。

## 常见问题

- 如果运行时报 `deepagents` 缺失，请确认已安装 `ksadk[deepagents]` 或 `ksadk[all]`。
- 如果没有模型 key，请先运行 `uv run python demo.py`。
- 如果要保证报告事实可靠，请不要让模型脱离引用材料发挥。
- 如果要开源，请确认 fixture 不包含客户数据或内部地址。
