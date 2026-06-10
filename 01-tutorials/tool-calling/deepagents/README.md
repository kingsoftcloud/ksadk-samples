# 工具调用 Agent（Tool Calling）- DeepAgents

DeepAgents 工具调用示例，展示 `create_deep_agent()` 如何绑定 LangChain tools。

## 适用场景

- 想用 DeepAgents 快速构建带工具的 Agent。
- 想确认 KSADK 0.6.2 下 DeepAgents 0.6.x 的工具绑定方式。
- 想比较 DeepAgents 与 LangChain、LangGraph 工具调用写法的差异。

## 你会看到什么

- `@tool` 包装 `calculate` 和 `get_weather`。
- `create_deep_agent(model=..., tools=[...], system_prompt=...)` 创建图。
- `root_agent` 是 DeepAgents 返回的 LangGraph 编译图。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

稍后在样例目录复制并编辑 `.env`，模型需要支持工具调用。

## 本地运行

```bash
cd 01-tutorials/tool-calling/deepagents
cp ../../../.env.example .env
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

观察 DeepAgents 是否调用工具并把工具结果整理成中文回复。

## 部署

```bash
uv run agentengine deploy .
```

部署前配置云账号 AK/SK，并先跑通本地命令。

## 示例问题

```text
帮我计算 128 * 7 + 42，并查询深圳天气。
```

## 常见问题

- DeepAgents 0.6.x 使用 `system_prompt` 参数。
- 如果模型不支持工具调用，示例可能只返回普通文本。
- 天气工具是静态示例，便于稳定复现。
