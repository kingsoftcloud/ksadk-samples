# 长任务恢复 Agent

这个目录聚合 Long Task Resume 的四种框架写法。长任务恢复是横向 Runtime 能力样例，重点演示 checkpoint 列表、ResumeRun、tool receipt 去重、CancelRun，以及未配置持久化后端时的降级说明。

## 适用场景

- Agent 需要执行研究、报表、代码修复、数据分析等长时间任务。
- 用户可能关闭 Web UI、取消任务，或者运行时因为网络/进程重启中断。
- 恢复执行时必须知道哪些工具调用已经完成，避免重复扣费、重复写文件或重复写入工作区。
- 团队想对比 LangGraph、ADK、LangChain、DeepAgents 在同一个 Runtime 能力上的工程组织方式。

## 如何选择

| 框架 | 目录 | 适合用户 |
| --- | --- | --- |
| LangGraph | [langgraph](langgraph/README.md) | 需要显式状态图、节点拆分和恢复编排的用户。 |
| ADK | [adk](adk/README.md) | 想按 Google ADK 风格组织工具和 Agent 的用户。 |
| LangChain | [langchain](langchain/README.md) | 已有 LangChain 链路，希望快速接入 KSADK 运行时的用户。 |
| DeepAgents | [deepagents](deepagents/README.md) | 想用更高层 Agent 抽象表达长任务恢复流程的用户。 |

## 环境准备

在仓库根目录准备依赖：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

每个子目录都是独立 Agent 工程，包含 `README.md`、`.env.example`、`agent.py`、`agentengine.yaml`、`requirements.txt`、`demo.py` 和 `smoke.py`。

## 本地运行

以 LangGraph 版本为例：

```bash
cd 02-use-cases/long-task-resume/langgraph
cp .env.example .env
uv pip install -r requirements.txt
uv run python demo.py
uv run python smoke.py
```

其他框架版本只需要把最后一级目录替换为 `adk`、`langchain` 或 `deepagents`。

## Web UI 调试

进入任一子目录后启动 Web UI：

```bash
uv run agentengine web .
```

推荐提问：

```text
调研国产 AI Agent Runtime 的市场格局、竞品、落地风险和下一步建议
```

LangGraph 版本会启动一个后台长任务，阶段完成后在 Web UI 的“会话恢复区”展示真实 LangGraph checkpoint。你可以在运行中继续普通对话，也可以点击取消，让后台任务停在最近 checkpoint 后再 ResumeRun。其他框架版本主要用于对比组织方式，恢复语义以各自 README 为准。

## 部署

进入任一子目录后部署：

```bash
uv run agentengine deploy .
```

部署前请确认 session/checkpoint backend 已按生产要求配置。公开样例不会携带真实 DSN、账号、token 或内部环境地址。

## 示例问题

- `调研国产 AI Agent Runtime 的市场格局、竞品、落地风险和下一步建议。`
- `如果用户取消了任务，ResumeRun 还应该继续跑吗？`
- `tool receipt 怎么避免重复调用 web_search、web_fetch 或 Workspace？`

## 配置边界

离线 demo 默认使用 fixture，不需要数据库、模型 key 或云账号。要接入真实长任务恢复能力时，再配置 session/checkpoint 持久化：

```bash
KSADK_SESSION_BACKEND=postgres
KSADK_SESSION_DSN=postgresql://<user>:<password>@<postgres-host>:5432/<database>
KSADK_SESSION_NAMESPACE=long_task_resume_demo
```

这些变量是当前 KSADK session/checkpoint 口径，不是 Skill Runtime 或 Sandbox 变量。Skill Runtime 的 template 配置请使用 `KSADK_SANDBOX_TEMPLATE_ID`，不要把长任务持久化配置和 E2B sandbox 配置混在一起。

## 验证建议

每个子目录都包含 `demo.py` 和 `smoke.py`：

- `demo.py` 展示一段可读的恢复说明。
- `smoke.py` 验证 `run_id`、`checkpoint_id`、`resume_attempt_id`、`cancel_status` 和 `duplicate_tool_count`。
- README 中会说明 checkpoint 列表、ResumeRun、tool receipt、CancelRun 和降级行为。

## 常见问题

**为什么不把四个版本平铺在 `02-use-cases` 下面？**

Long Task Resume 是一个能力场景，不是四个独立业务场景。放在同一个目录下更容易对比不同框架的写法，也能减少 README 导航噪声。

**只运行 demo 需要 Postgres 吗？**

不需要。公开样例默认使用本地 fixture，方便用户 clone 后直接运行；Postgres 只用于生产级 session/checkpoint 持久化。

**tool receipt 是什么？**

它是恢复执行时的幂等凭证，用来判断某个外部工具调用是否已经完成，避免 ResumeRun 后重复扣费、重复写文件或重复写入工作区。
