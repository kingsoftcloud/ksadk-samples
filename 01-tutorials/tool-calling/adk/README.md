# 工具调用 Agent（Tool Calling）- ADK

ADK 工具调用示例，展示如何把普通 Python 函数注册为 Agent 可调用工具。

## 适用场景

- 想学习 ADK Agent 如何调用业务函数。
- 想验证 KSADK 能否把工具调用事件透传到本地 CLI 和 Web UI。
- 想从计算器、天气查询这类确定性工具开始扩展示例。

## 你会看到什么

- `calculate(expression)` 演示受限数学表达式计算。
- `get_weather(city)` 演示查询静态示例天气数据。
- `root_agent` 是 `google.adk.agents.Agent`，并通过 `tools=[...]` 绑定工具。

## 环境准备

在 `ksadk-samples` 仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

编辑 `.env`，填写模型配置。

## 本地运行

```bash
cd 01-tutorials/tool-calling/adk
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

在 Web UI 中提问后，可以观察模型是否先调用工具，再用中文总结结果。

## 部署

```bash
uv run agentengine deploy .
```

部署前请配置 `KSYUN_ACCESS_KEY` 和 `KSYUN_SECRET_KEY`，并先完成本地 smoke。

## 示例问题

```text
帮我计算 128 * 7 + 42，并查询深圳天气。
```

## 常见问题

- 如果模型直接回答而不调用工具，可以把问题写得更明确，例如“必须调用工具计算”。
- `calculate` 只允许少量安全内置函数，不适合作为通用 Python 执行器。
- 天气数据是静态示例，不会访问真实天气服务。
