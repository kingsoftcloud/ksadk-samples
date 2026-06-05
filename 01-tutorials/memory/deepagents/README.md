# Memory - DeepAgents

DeepAgents 记忆示例，展示如何把保存和读取记忆的工具交给 DeepAgents 调用。

## 适用场景

- 想用 DeepAgents 构建带记忆工具的 Agent。
- 想比较 DeepAgents 与 ADK、LangChain、LangGraph 的记忆写法。
- 想验证 KSADK 0.6.2 下 DeepAgents 0.6.x 的工具绑定方式。

## 你会看到什么

- `save_memory` 和 `load_memory` 都用 `@tool` 包装。
- `create_deep_agent()` 通过 `tools=[...]` 绑定记忆工具。
- 系统提示通过 `system_prompt` 传入。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写模型配置。DeepAgents 记忆示例需要模型支持工具调用。

## 本地运行

```bash
cd 01-tutorials/memory/deepagents
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

在同一个会话里连续提问，观察 DeepAgents 是否调用保存和读取工具。

## 部署

```bash
uv run agentengine deploy .
```

部署前配置云账号 AK/SK。生产环境应替换为可审计、可隔离的长期记忆存储。

## 示例问题

```text
请记住我喜欢 Python 和 LangGraph。
```

```text
我之前喜欢什么？
```

## 常见问题

- DeepAgents 0.6.x 使用 `system_prompt`，不是 `instructions`。
- 如果模型没有调用记忆工具，尝试明确要求“请调用工具保存这条偏好”。
- 默认本地记忆不需要云资源，但也不适合作为生产持久化方案。
