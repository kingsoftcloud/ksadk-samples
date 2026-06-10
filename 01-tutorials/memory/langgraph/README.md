# 记忆增强 Agent（Memory）- LangGraph

LangGraph 记忆示例，展示如何把用户 ID、平台记忆和本地记忆放入图状态。

## 适用场景

- 想用 LangGraph 管理记忆相关状态。
- 想了解 `ksadk_prepare_state` 如何从 `session_context` 提取用户上下文。
- 想在图节点中控制保存和读取记忆的时机。

## 你会看到什么

- `AgentState` 包含 `query`、`user_id`、`memory_context` 和 `answer`。
- `ksadk_prepare_state` 从平台上下文中读取用户 ID。
- `answer` 节点在用户要求记住时保存本地记忆，再生成回答。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写模型配置。默认本地记忆不依赖云资源。

## 本地运行

```bash
cd 01-tutorials/memory/langgraph
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 适合验证同一用户上下文下的多轮记忆读取。

## 部署

```bash
uv run agentengine deploy .
```

部署前配置云账号 AK/SK。上线前请确认记忆存储是否满足业务的数据保留和隐私要求。

## 示例问题

```text
请记住我喜欢 Python 和 LangGraph。
```

```text
我之前喜欢什么？
```

## 常见问题

- 如果状态字段报错，检查 `AgentState` 和 `ksadk_prepare_state` 是否同步更新。
- 如果要改成平台长期记忆，可以把 `memory_context` 作为图状态继续传递。
- 本地记忆适合 demo，不代表生产级多租户隔离方案。
