# Hello World - DeepAgents

最小 DeepAgents 示例。`create_deep_agent()` 返回 LangGraph 图，因此 KSADK 可以通过 `framework: deepagents` 运行它。

## 适用场景

- 想体验 DeepAgents 的最小 Agent 结构。
- 想确认 KSADK 0.6.2 与 DeepAgents 0.6.x 的基础兼容性。
- 想从空工具列表开始，逐步扩展 DeepAgents 示例。

## 你会看到什么

- `agent.py` 调用 `create_deep_agent()`。
- 系统提示通过 `system_prompt` 传入。
- `root_agent` 是编译后的 LangGraph 图。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写 `.env` 中的模型配置。DeepAgents 依赖支持工具调用的模型。

## 本地运行

```bash
cd 01-tutorials/hello-world/deepagents
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以观察 DeepAgents 的消息输出。

## 部署

```bash
uv run agentengine deploy .
```

部署前先确认本地运行成功，并配置云账号 AK/SK。

## 示例问题

```text
你好，介绍一下你自己。
```

## 常见问题

- DeepAgents 0.6.x 使用 `system_prompt`，不是旧版本示例中的 `instructions`。
- 如果模型不支持工具调用，复杂 DeepAgents 示例可能失败；本 hello-world 不绑定业务工具。
- 如果要看工具调用，请继续看 `01-tutorials/tool-calling/deepagents`。
