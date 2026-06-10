# 记忆增强 Agent（Memory）- LangChain

LangChain 记忆示例，展示如何在 `ksadk_prepare_input` 中合并平台记忆和本地记忆。

## 适用场景

- 想用 LangChain Runnable 读取记忆上下文。
- 想理解 `session_context` 如何参与输入准备。
- 想先使用本地记忆完成最小闭环。

## 你会看到什么

- 用户输入包含“记住”时，`ksadk_prepare_input` 会保存本地记忆。
- 每次调用都会读取本地记忆，并合并可选的 `memory_context`。
- `root_agent` 是 `prompt | model | StrOutputParser()` 组成的 LangChain Runnable。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写模型配置。默认本地记忆不需要云端长期记忆配置。

## 本地运行

```bash
cd 01-tutorials/memory/langchain
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中连续提问，可以验证 `ksadk_prepare_input` 是否把记忆内容拼入提示词。

## 部署

```bash
uv run agentengine deploy .
```

部署前配置云账号 AK/SK。生产环境建议把本地记忆替换为平台长期记忆或业务数据库。

## 示例问题

```text
请记住我喜欢 Python 和 LangGraph。
```

```text
我之前喜欢什么？
```

## 常见问题

- 如果记忆没有生效，先确认第一轮问题中包含“记住”。
- 如果接入平台长期记忆，可从 `session_context["memory_context"]` 读取平台注入的文本。
- 本示例把记忆逻辑放在输入准备阶段，适合 LangChain Runnable 的简单场景。
