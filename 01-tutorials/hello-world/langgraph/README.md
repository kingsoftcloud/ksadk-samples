# Hello World - LangGraph

最小 LangGraph Agent 示例，用一个单节点 `StateGraph` 展示 KSADK 的 LangGraph 入口约定。

## 适用场景

- 想用 LangGraph 写第一个 KSADK Agent。
- 想了解 `ksadk_prepare_state` 如何初始化图状态。
- 想确认 `framework: langgraph` 的最小可运行结构。

## 你会看到什么

- `AgentState` 保存 `query` 和 `answer`。
- `answer` 节点调用模型并返回回答。
- `root_agent = workflow.compile()` 是 KSADK 运行的 LangGraph 图对象。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写 `.env` 中的模型配置。

## 本地运行

```bash
cd 01-tutorials/hello-world/langgraph
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 适合观察多轮输入如何进入 `ksadk_prepare_state`。

## 部署

```bash
uv run agentengine deploy .
```

部署前确认 AK/SK 已配置，并先完成一次本地 smoke。

## 示例问题

```text
你好，介绍一下你自己。
```

## 常见问题

- 如果状态字段报错，检查 `AgentState` 和 `ksadk_prepare_state` 返回值是否一致。
- 如果模型请求失败，检查 `OPENAI_BASE_URL` 和 `OPENAI_MODEL_NAME`。
- 如果要学习工具节点，请继续看 `01-tutorials/tool-calling/langgraph`。
