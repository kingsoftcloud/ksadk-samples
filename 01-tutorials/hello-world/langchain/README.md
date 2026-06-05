# Hello World - LangChain

最小 LangChain Runnable 示例，用来展示 KSADK 如何运行一个普通 LangChain 链。

## 适用场景

- 想用 LangChain 写最小对话 Agent。
- 想了解 `ksadk_prepare_input` 如何把 AgentEngine 输入转成 LangChain 输入。
- 想确认 KSADK 0.6.2 下 LangChain 1.x 的基础链路是否可用。

## 你会看到什么

- `agent.py` 使用 `ChatPromptTemplate`、`make_langchain_chat_model()` 和 `StrOutputParser()`。
- `ksadk_prepare_input(payload, session_context)` 从 `payload["input"]` 提取用户输入。
- `root_agent` 是一个 LangChain Runnable，可以被 KSADK 直接调用。

## 环境准备

在 `ksadk-samples` 仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

编辑 `.env`，至少填写模型相关配置。

## 本地运行

```bash
cd 01-tutorials/hello-world/langchain
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 会把用户输入传给 `ksadk_prepare_input`，再进入 LangChain Runnable。

## 部署

```bash
uv run agentengine deploy .
```

部署前需要在 `.env` 中配置云账号 AK/SK，并确认账号有 AgentEngine 权限。

## 示例问题

```text
你好，介绍一下你自己。
```

## 常见问题

- 如果回复为空，先确认模型服务兼容 OpenAI Chat API。
- 如果导入 LangChain 失败，重新执行 `uv pip install -r requirements.txt`。
- 如果要扩展工具调用，请参考 `01-tutorials/tool-calling/langchain`。
