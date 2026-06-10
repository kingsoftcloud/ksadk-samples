# 工具调用 Agent（Tool Calling）- LangGraph

LangGraph 工具调用示例，展示 `StateGraph`、`ToolNode` 和条件边的最小组合。

## 适用场景

- 想学习 LangGraph 中最基础的工具调用循环。
- 想了解如何根据 `tool_calls` 决定是否进入工具节点。
- 想在 KSADK 中运行可解释的 LangGraph 图。

## 你会看到什么

- `AgentState.messages` 通过 `add_messages` 自动合并消息。
- `call_model` 节点调用绑定工具后的模型。
- `should_continue` 根据最后一条消息判断进入 `tools` 还是结束。
- `ToolNode(tools)` 负责执行工具。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

稍后在样例目录复制并编辑 `.env`，确保模型支持 tool calling。

## 本地运行

```bash
cd 01-tutorials/tool-calling/langgraph
cp ../../../.env.example .env
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 适合观察模型消息、工具消息和最终回复的顺序。

## 部署

```bash
uv run agentengine deploy .
```

部署前请先完成本地 smoke，并配置云账号 AK/SK。

## 示例问题

```text
帮我计算 128 * 7 + 42，并查询深圳天气。
```

## 常见问题

- 如果图直接结束，通常是模型没有返回 `tool_calls`。
- 如果要增加工具，把函数加入 `tools` 列表并重新 `bind_tools`。
- `calculate` 是演示工具，不要替代生产环境表达式执行沙箱。
