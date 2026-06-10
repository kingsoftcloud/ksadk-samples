# 基础 Agent（Hello World）- ADK

最小 ADK Agent 示例，用来确认 KSADK、模型配置和 AgentEngine 本地运行链路是否正常。

## 适用场景

- 第一次运行 KSADK samples。
- 想了解 `framework: adk` 的最小文件结构。
- 想验证 ADK Agent 能否被 `agentengine run`、`agentengine web` 和 `agentengine deploy` 识别。

## 你会看到什么

- `agent.py` 定义一个 `google.adk.agents.Agent`。
- `agentengine.yaml` 声明 `entry_point: agent.py` 和 `agent_variable: root_agent`。
- Agent 使用仓库公共模型配置 `common.model_config.make_adk_litellm_model()`。

## 环境准备

在 `ksadk-samples` 仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

编辑 `.env`，至少填写 `OPENAI_API_KEY`、`OPENAI_BASE_URL` 和 `OPENAI_MODEL_NAME`。

## 本地运行

```bash
cd 01-tutorials/hello-world/adk
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

打开浏览器后输入示例问题，确认回复中说明自己运行在 ADK 示例中。

## 部署

部署前在 `.env` 中配置 `KSYUN_ACCESS_KEY` 和 `KSYUN_SECRET_KEY`：

```bash
uv run agentengine deploy .
```

## 示例问题

```text
你好，介绍一下你自己。
```

## 常见问题

- 如果提示模型鉴权失败，先检查 `.env` 中的 OpenAI 兼容模型配置。
- 如果提示找不到 `root_agent`，检查 `agentengine.yaml` 的 `agent_variable` 是否仍为 `root_agent`。
- 如果部署失败，先确认本地 `uv run agentengine run -i .` 已经可以正常对话。
