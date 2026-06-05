# Memory - ADK

ADK 记忆示例，展示如何用本地记忆工具保存和读取用户偏好。

## 适用场景

- 想学习 Agent 如何在多轮对话中记住用户偏好。
- 想先用本地文件式记忆跑通流程，再扩展到平台长期记忆。
- 想了解 ADK Agent 如何绑定读写类工具。

## 你会看到什么

- `save_memory(content, user_id)` 保存一条本地记忆。
- `load_memory(query, user_id)` 读取本地记忆。
- `root_agent` 是 ADK Agent，通过 `tools=[save_memory, load_memory]` 绑定工具。

## 环境准备

在 `ksadk-samples` 仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写 `.env` 中的模型配置。默认本地记忆不需要云资源。

## 本地运行

```bash
cd 01-tutorials/memory/adk
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

建议在同一个会话里连续发送两条示例问题，观察保存和读取效果。

## 部署

```bash
uv run agentengine deploy .
```

部署前配置云账号 AK/SK。本地记忆示例主要用于教学，生产环境建议接入平台长期记忆或外部存储。

## 示例问题

```text
请记住我喜欢 Python 和 LangGraph。
```

```text
我之前喜欢什么？
```

## 常见问题

- 如果第二个问题没有读到记忆，确认是否在同一运行环境和同一用户上下文中测试。
- 默认 `user_id` 是 `local-user`；接入真实用户系统时应从平台上下文传入用户 ID。
- 本地记忆适合演示，不适合作为生产环境的持久化方案。
