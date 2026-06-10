# 工具调用 Agent（Tool Calling）- LangChain

LangChain 工具调用示例，使用 LangChain 1.x 的 `create_agent` 绑定工具。

## 适用场景

- 想用 LangChain 1.x 写工具调用 Agent。
- 想了解 KSADK 0.6.2 下推荐的 LangChain agent 创建方式。
- 想把本地业务函数逐步接入 AgentEngine。

## 你会看到什么

- `@tool` 包装 `calculate` 和 `get_weather`。
- `ksadk_prepare_input` 把 AgentEngine 输入映射成 LangChain 输入。
- `root_agent = create_agent(...)`，不再使用旧版 `AgentExecutor`。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

稍后在样例目录复制并编辑 `.env`。工具调用示例需要模型支持 tool calling。

## 本地运行

```bash
cd 01-tutorials/tool-calling/langchain
cp ../../../.env.example .env
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 里可以观察工具调用输入、输出和最终自然语言回答。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认本地运行成功，并配置云账号 AK/SK。

## 示例问题

```text
帮我计算 128 * 7 + 42，并查询深圳天气。
```

## 常见问题

- LangChain 1.x 不再从 `langchain.agents` 导出 `AgentExecutor` 和 `create_tool_calling_agent`。
- 如果模型不支持 tool calling，工具可能不会被调用。
- 示例天气是静态数据，方便本地复现，不依赖外部服务。
