# 长任务恢复 Agent - ADK

这个 demo 演示长任务 Agent 如何在中断后恢复执行：读取 checkpoint 列表、发起 ResumeRun、检查 tool receipt、处理 CancelRun，并在未配置持久化组件时给出清晰降级说明。它是一个多文件 ADK Agent 工程，不是单文件脚本；默认使用本地 fixture，方便公开仓库用户 clone 后直接运行。

## 适用场景

- Agent 需要执行研究、报表生成、代码修复、数据分析等耗时任务。
- 任务中途可能因为进程重启、网络抖动、用户关闭 Web UI 或主动取消而中断。
- 恢复后必须避免重复调用外部工具，例如重复扣费、重复写文件、重复提交工单。
- 你希望对比 LangGraph / ADK / LangChain / DeepAgents 在长任务恢复场景下的工程写法。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | ADK `root_agent` 入口。 |
| `tools.py` | 本地 fixture 和长任务恢复工具函数，生产环境可替换为数据库和平台 API。 |
| `demo.py` | 离线演示，不需要模型 key、数据库或云账号。 |
| `smoke.py` | 最小 e2e 烟测，验证恢复字段和 tool receipt 去重字段。 |
| `.env.example` | session backend、DSN 和 namespace 示例。 |
| `agentengine.yaml` | AgentEngine / KSADK 运行配置。 |
| `requirements.txt` | 当前框架运行依赖。 |

## 环境准备

推荐在仓库根目录安装开发依赖：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

进入样例目录后复制环境变量模板：

```bash
cd 02-use-cases/long-task-resume/adk
cp ../../../.env.example .env
uv pip install -r requirements.txt
```

如果只是运行离线 demo，可以不填写真实数据库。需要演示长任务持久化配置时，可以把本目录 `.env.example` 中的 session 变量追加到 `.env`。生产环境建议配置：

```bash
KSADK_SESSION_BACKEND=postgres
KSADK_SESSION_DSN=postgresql://<user>:<password>@<postgres-host>:5432/<database>
KSADK_SESSION_NAMESPACE=long_task_resume_demo
```

变量含义：

| 变量 | 含义 |
| --- | --- |
| `KSADK_SESSION_BACKEND` | session/checkpoint 持久化后端，生产建议使用 `postgres`。 |
| `KSADK_SESSION_DSN` | 后端连接串；公开样例只放占位符，不写真实账号。 |
| `KSADK_SESSION_NAMESPACE` | 长任务状态隔离命名空间，建议按应用或租户拆分。 |
| `LONG_TASK_RESUME_DEMO_MODE` | 本地演示模式，默认 `fixture`，不访问外部服务。 |

## 本地运行

先看离线输出：

```bash
uv run python demo.py
```

运行最小烟测：

```bash
uv run python smoke.py
```

启动本地 OpenAI-compatible 服务：

```bash
uv run agentengine run -i .
```

另开终端验证：

```bash
curl http://localhost:8000/health
curl http://localhost:8000/v1/models
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以提问：

```text
帮我恢复一个中断的长任务，并说明哪些工具调用不应该重复执行。
```

你应该能看到 `checkpoint 列表`、`ResumeRun`、`tool receipt`、`CancelRun` 和 `降级说明` 五个关键部分。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认：

- 已配置持久化 session backend。
- checkpoint、tool receipt 和 cancel 状态使用同一个 namespace。
- tool receipt key 稳定且可幂等，例如按业务对象、工具名和参数摘要生成。
- 外部工具调用必须在写入 receipt 后再返回成功状态，避免恢复时误判。

## 示例问题

- `帮我恢复一个中断的长任务，并说明哪些工具调用不应该重复执行。`
- `用户取消了昨天的研究任务，现在状态应该怎么判断？`
- `如果分析工具已经跑完，ResumeRun 后怎么避免重复执行？`

## checkpoint 列表

本 demo 的 checkpoint 由 `tools.py` 的 `build_checkpoints` 生成。真实接入时，建议把 checkpoint 设计为可审计事件：

- `checkpoint_id`：恢复点 ID。
- `step_id`：业务阶段，例如收集需求、运行分析、生成交付物。
- `status`：阶段状态，例如 completed、running、ready_to_resume、cancelled。
- `summary`：给用户和运维看的阶段摘要。

## ResumeRun

ResumeRun 的核心不是“重新跑一遍”，而是：

1. 根据 `run_id` 找到最近可恢复 checkpoint。
2. 为本次恢复生成新的 `resume_attempt_id`。
3. 查询 tool receipt，跳过已经成功的工具调用。
4. 只执行缺失阶段，并继续写入 checkpoint。

## tool receipt

tool receipt 用来证明某个外部工具调用已经完成。典型字段包括：

- `receipt_key`：幂等键，例如 `workspace:report:v1`。
- `tool_name`：工具名，例如 `sandbox.run`。
- `run_id`：所属长任务。
- `resume_attempt_id`：本次恢复尝试。
- `status`：recorded、skipped_duplicate、failed。

## CancelRun

CancelRun 建议做成协作式取消：

- API 或 Web UI 只写入取消意图。
- 长任务在每个工具边界检查取消状态。
- 已经开始且不可回滚的工具调用要继续写 receipt，避免下次恢复重复执行。

## 降级说明

- 未配置 `KSADK_SESSION_BACKEND` 时，本 demo 使用 fixture，仍然可以观察恢复流程。
- 未配置真实 Sandbox 时，不会执行外部命令，只展示 receipt 去重。
- 未配置 Workspace 时，不会写入真实文件，只展示交付物写回阶段。
- 未配置模型 key 时，`demo.py` 和 `smoke.py` 仍可运行；`agentengine run/web` 是否需要模型取决于你的 Agent 逻辑。

## 常见问题

- **为什么不直接重跑任务？** 长任务往往包含付费 API、文件写入、工单提交或状态变更，重复执行会产生副作用。
- **checkpoint 应该存在哪里？** 生产建议放在持久化 session store，并按租户或应用 namespace 隔离。
- **tool receipt 和日志有什么区别？** 日志用于观察，receipt 用于恢复决策；恢复逻辑不能只依赖文本日志。
- **这个 demo 会访问真实平台吗？** 默认不会。它只使用公开 fixture，适合作为开源样例和本地教学工程。
