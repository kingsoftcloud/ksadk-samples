# 长任务恢复 Agent - LangGraph

这个 demo 用于长任务恢复 E2E：通过 LangGraph checkpointer 持久化通用 DeepResearch 研究任务，演示 Web UI 里选择 LangGraph 状态快照后，通过 ResumeRun 沿用同一个 run_id 继续执行。它是一个多文件 LangGraph Agent 工程，不是单文件脚本；Web/API 路径使用自定义 Runner 接入真实 session event，离线路径保留 fixture，方便公开仓库用户 clone 后直接运行。

恢复路径使用 LangGraph 的 `StateSnapshot.config`，即 `configurable.thread_id` + 可选 `checkpoint_ns` + `checkpoint_id`，并调用 `graph.astream(None, config=checkpoint_config, stream_mode="updates")` 从 checkpoint 后的节点继续。平台写入的 `run_checkpoint` 只是 UI / 审计索引事件，里面保存 `framework_ref.langgraph` 和业务摘要；真实 checkpoint 仍由 LangGraph checkpointer 保存。

本地默认使用 `InMemorySaver` 做交互演示，不访问外部数据库；预发或生产把 `LONG_TASK_RESUME_DEMO_MODE=postgres` 后会使用 `AsyncPostgresSaver` 和真实 PG。离线的 `demo.py` / `smoke.py` 仍使用 `workflow.py` 和 `tools.py` fixture，方便快速查看报告内容；真实 checkpoint resume / runtime cancel 请用 `agentengine run/web` 或部署到目标 pod 后验证。

## 图结构

Web/API 路径不是简单的顺序假进度条。`agent.py` 中的主图和子图组合如下：

| 层级 | LangGraph 用法 | 说明 |
| --- | --- | --- |
| 主图 | `StateGraph(ReportState)` + checkpoint | 7 个可恢复业务安全点，每个阶段完成后写入 LangGraph `StateSnapshot`。 |
| web_search 子图 | `add_conditional_edges(START, fan_out_queries)` + `Send` | 把研究计划里的多个 query 并行分发给 `web_search_agent`，汇总候选来源。 |
| 分析子图 | `Send` map-reduce | 并行运行 market、technical、risk 三个 reviewer，基于证据表做 LLM 交叉分析。 |
| 条件路由 | `add_conditional_edges("analyze_findings", ...)` | 根据状态决定是否进入批判性质检；默认进入 `critic_review`，并在分析阶段模拟一次外部服务失败。 |
| 恢复执行 | `graph.astream(None, config=checkpoint_config, stream_mode="updates")` | ResumeRun 使用 checkpoint config 续跑，不重放 checkpoint 前的节点和工具副作用。 |

Web UI 展示的是主图业务安全点的 `run_checkpoint` 索引。子图内部的多 Agent 执行摘要会写入最终报告的“LangGraph 子图和多 Agent”章节，便于演示复杂研究编排。

## 开发者学习路径

这个样例的重点不是固定的“AI Agent Runtime 调研”题目，而是教你写一个可恢复的长任务 Agent。建议按下面顺序阅读和改造：

1. 先看 `REPORT_STAGES`：这里定义业务安全点、阶段标题、工具名、receipt key、用户可见摘要和恢复后的下一步。开发自己的长任务时，先把阶段拆成“完成后可安全恢复”的边界。
2. 再看 `_compile_graph`：这里把主图节点、条件路由和最终报告节点串起来。checkpoint 由 LangGraph checkpointer 自动写入，不要自己伪造 checkpoint 本体。
3. 再看 `_build_web_search_subgraph` 和 `_build_analysis_subgraph`：这里演示 `Send` 并行 fan-out、子图汇总和多 reviewer 分析。业务复杂度可以继续加子图，但主图恢复点要保持清晰。
4. 再看 `_stream_checkpoint_resume`：ResumeRun 使用 `graph.astream(None, config=checkpoint_config, stream_mode="updates")` 续跑。`input=None` 是关键，它表示从 LangGraph checkpoint 继续，而不是重新提交用户问题。
5. 最后看 `_run_background_job`：后台任务每个阶段完成后写入 `run_checkpoint` session event。这个事件只是 Web UI 和审计索引，里面保存 `framework_ref.langgraph`；真实状态仍在 LangGraph checkpointer。

## 改造成你的业务 Agent

常见改造点如下：

| 目标 | 改哪里 | 保留什么 |
| --- | --- | --- |
| 换业务场景 | `REPORT_STAGES`、`_initial_state`、`_run_write_report_stage` | 每个阶段必须有稳定 `receipt_key`。 |
| 接企业搜索 | `_web_search` 或 `DEEPRESEARCH_WEB_SEARCH_URL` | 搜索成功后再进入 checkpoint，避免恢复后重复检索。 |
| 接浏览器抓取或知识库 | `_web_fetch`、`_run_fetch_sources_stage` | 工具输出写入 state，再由 checkpointer 持久化。 |
| 接真实 LLM 分析 | `_llm_or_fallback`、`_run_analysis_stage` | LLM 调用失败时保留最近 checkpoint，恢复后从当前节点继续。 |
| 加更多 Agent / 子图 | `_build_web_search_subgraph`、`_build_analysis_subgraph` 或新增子图 | 子图内部可以复杂，主图安全点不要碎到 UI 难以理解。 |
| 接生产 PG | `LONG_TASK_RESUME_DEMO_MODE=postgres`、`KSADK_LANGGRAPH_CHECKPOINT_DSN` | `thread_id/checkpoint_ns/checkpoint_id` 必须来自 `StateSnapshot.config`。 |
| 接 Runtime CancelRun | `request_cancel`、`_run_background_job` 的工具边界检查 | 取消只写意图；不可回滚工具完成后仍要写 receipt。 |

不要把离线 `tools.py` 的 fixture 当成生产恢复实现。`tools.py` 用于公开仓库快速展示报告结构；真正可恢复的 LangGraph 路径在 `agent.py`。

## 适用场景

- Agent 需要执行研究、Deep Research 报告生成、代码修复、数据分析等耗时任务。
- 任务中途可能因为进程重启、网络抖动、用户关闭 Web UI 或主动取消而中断。
- 恢复后必须避免重复调用外部工具，例如重复扣费、重复写文件、重复写入工作区。
- 你希望在本地先理解 checkpoint / ResumeRun / CancelRun 的工程边界，再接入真实 AgentEngine session store。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | Web / API E2E 入口，自定义 `LongTaskE2ERunner`，本地使用 LangGraph `InMemorySaver`，PG 模式使用 `AsyncPostgresSaver`。 |
| `workflow.py` | 离线 fixture 编排：加载 checkpoint、恢复执行、检查取消状态、渲染结果。 |
| `tools.py` | 离线 fixture 和长任务恢复工具函数，生产环境可替换为数据库和平台 API。 |
| `demo.py` | 离线演示，不需要模型 key、数据库或云账号。 |
| `smoke.py` | 最小 e2e 烟测，验证恢复字段和 tool receipt 去重字段。 |
| `e2e_http.py` | 本地/预发 HTTP E2E：流式启动后台任务、CancelRun、PreviewCheckpointResume、ResumeRun。 |
| `pg_smoke.py` | 可选 Postgres smoke，验证用户自己的 DSN 可连接、可建表、可读写。 |
| `tests/test_agent_behavior.py` | 行为测试，确认普通聊天不伪造 checkpoint、恢复用 LangGraph checkpoint config。 |
| `.env.example` | session backend、DSN 和 namespace 示例。 |
| `agentengine.yaml` | AgentEngine / KSADK 运行配置。 |

## 环境准备

推荐在仓库根目录安装开发依赖：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

进入样例目录后复制环境变量模板：

```bash
cd 02-use-cases/long-task-resume/langgraph
cp .env.example .env
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
| `KSADK_LANGGRAPH_CHECKPOINT_DSN` | LangGraph Postgres checkpointer 连接串；PG 模式优先使用它，未配置时回退到 `KSADK_SESSION_DSN`。 |
| `LONG_TASK_RESUME_DEMO_MODE` | 本地演示模式，默认 `fixture`，使用 LangGraph `InMemorySaver`；设为 `postgres` 后连接真实 PG。 |
| `LONG_TASK_STAGE_DELAY_SECONDS` | 每个业务阶段的演示延迟。Web UI 人工演示建议设为 `6`，避免还没点取消任务就跑完。 |
| `DEEPRESEARCH_WEB_SEARCH_URL` | 可选 web_search HTTP 接口，期望 `GET ?q=<query>&max_results=<n>` 返回 `results` 列表；未配置时使用可运行降级结果。 |

## 本地运行

先看离线输出：

```bash
uv run python demo.py
```

运行最小烟测：

```bash
uv run python smoke.py
```

运行行为测试：

```bash
uv run pytest tests/test_agent_behavior.py -q
```

## 可选真实 PG smoke

公开样例默认不会连接真实数据库。需要验证自己的 Postgres 是否能作为长任务持久化后端时，先安装 PG 客户端依赖，并显式切换模式：

```bash
uv pip install "psycopg[binary]>=3.2"
export LONG_TASK_RESUME_DEMO_MODE=postgres
export KSADK_SESSION_DSN='postgresql://<user>:<password>@<postgres-host>:5432/<database>'
export KSADK_SESSION_NAMESPACE=long_task_resume_demo
uv run python pg_smoke.py
```

`pg_smoke.py` 会创建样例专用表 `long_task_resume_smoke`，写入并读取一条 checkpoint/receipt 记录，然后清理本次 smoke 数据。脚本不会打印密码，也不会内置任何真实 PG 地址。它只验证数据库连接和建表权限；完整的 checkpoint resume / runtime cancel E2E 仍应在目标运行环境用 `agent.py` 执行。

如果本地访问 PG 超时，把同一目录部署到预发算力 pod 后再跑；预发 pod 能访问内网 PG 时，Web UI 才能展示真实 checkpoint 列表。

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
LONG_TASK_STAGE_DELAY_SECONDS=6 uv run agentengine web .
```

Web UI 中可以提问：

```text
调研国产 AI Agent Runtime 的市场格局、竞品、落地风险和下一步建议
```

演示步骤：

1. 用 6 秒左右的阶段延迟启动 Web UI，方便人工在前几个 checkpoint 后观察、继续对话或点击取消。
2. 发送“调研国产 AI Agent Runtime 的市场格局、竞品、落地风险和下一步建议”。
3. Agent 立即返回后台 run_id 和后台 invocation_id，此后你可以继续普通对话；普通对话会调用模型，不会伪造 checkpoint。用户不需要说“执行长任务”，正常研究问题会触发后台 Deep Research。
4. Web UI 会订阅后台 invocation 的会话事件。后台任务每完成一个业务阶段，都会把 LangGraph checkpoint 的 `thread_id/checkpoint_id` 索引写入 `run_checkpoint` 事件，“会话恢复区”会实时出现状态快照和业务摘要。
5. 点击“取消运行并保留恢复点”后，前端会发送 CancelRun 并继续等待后台任务停在最近 checkpoint；等待恢复按钮可用后，选择任一 LangGraph 状态快照恢复。
6. ResumeRun 会用该快照索引里的 `framework_ref.langgraph` 构造 LangGraph checkpoint config，并以 `graph.astream(None, checkpoint_config, stream_mode="updates")` 继续执行。checkpoint 前的节点不会重跑；恢复输出会说明已跳过的阶段和复用的 tool receipt。

不要在原后台任务仍在运行时同时点击恢复同一个 run；真实产品路径应先 CancelRun、等待任务进入 `cancelled/failed`，再从最新 checkpoint 恢复。否则原任务和恢复任务会并发推进同一个 `thread_id`，UI 上会出现重复阶段，不能作为验收路径。

## HTTP E2E 验收

本地或预发服务启动后，可以用脚本验证真实 API 闭环：

```bash
LONG_TASK_E2E_BASE_URL=http://localhost:9876 uv run python e2e_http.py
```

脚本会执行：

1. 调 `/v1/responses` 流式启动后台 DeepResearch。
2. 等待至少两个 LangGraph checkpoint 写入 session event。
3. 调 `CancelRun`，等待后台 invocation 进入 `cancelled`。
4. 调 `PreviewCheckpointResume` 检查 run/checkpoint/receipt。
5. 调 `ResumeRun` 流式恢复，断言输出包含跳过阶段和 `deepresearch-report.md`。
6. 调 `ListSessionCheckpoints`，断言 checkpoint 列表没有空 stage/status。

本地 `agentengine web` / `agentengine run` 场景可以让脚本先调 `CreateSession`。预发 pod 内验收时，`/v1/responses` 通常会用运行时真实 `agent_id` 自动创建 session；此时 action API 也必须使用同一个 runtime agent id，否则 PG session backend 会拒绝后续 checkpoint 查询或取消请求。推荐在 pod 内这样跑：

```bash
LONG_TASK_E2E_BASE_URL=http://localhost:8080 \
LONG_TASK_E2E_AGENT_ID=<runtime-agent-id> \
LONG_TASK_E2E_SKIP_CREATE_SESSION=1 \
python e2e_http.py
```

如果通过公网 endpoint 验收，还需要按部署环境要求补充鉴权 header 或通过 `agentengine` CLI 代理访问；不要把真实 PG、模型 key、网关地址或公网鉴权 token 提交到公开样例。

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

- `调研国产 AI Agent Runtime 的市场格局、竞品、落地风险和下一步建议`
- `后台任务进度到哪了？`
- `普通对话：帮我解释一下 web_search 和 web_fetch 在 DeepResearch 里的区别`
- `用户取消了刚才的 DeepResearch 任务，现在状态应该怎么判断？`
- `如果 web_search 和 web_fetch 已经完成，ResumeRun 后怎么避免重复执行？`

## checkpoint 列表

`agent.py` 的 Web/API 路径使用 LangGraph 真实 checkpoint。每个 UI 状态快照来自 `run_checkpoint` 事件，事件中的 `framework_ref.langgraph` 保存了恢复所需的 `thread_id`、可选 `checkpoint_ns` 和 `checkpoint_id`。真实接入时，建议把 `run_checkpoint` 设计为可审计索引事件：

- `checkpoint_id`：恢复点 ID。
- `step_id`：业务阶段，例如规划研究问题、检索公开网页、抓取来源正文、筛选证据并去重、交叉分析发现、批判性质检、生成研究报告。
- `status`：阶段状态，例如 completed、running、ready_to_resume、cancelled。
- `summary`：给用户和运维看的阶段摘要。

## LangGraph ResumeRun

ResumeRun 的核心不是“重新跑一遍”，而是：

1. 根据 `run_id` 和 `checkpoint_id` 找到对应的 `run_checkpoint` 事件。
2. 从 `framework_ref.langgraph` 取出 `thread_id`、可选 `checkpoint_ns` 和 `checkpoint_id`。
3. 用这些字段构造 LangGraph checkpoint config，并以 `input=None` 继续执行。
4. 查询 tool receipt，标记已经成功的工具调用，避免重复检索证据、重复写文件或重复写报告。
5. 只执行 checkpoint 之后的节点，并继续写入新的 checkpoint。

## tool receipt

tool receipt 用来证明某个外部工具调用已经完成。典型字段包括：

- `receipt_key`：幂等键，例如 `deepresearch:report:v1`。
- `tool_name`：工具名，例如 `web.search`、`web.fetch`、`workspace.write`。
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
- 未配置真实 web_search / web_fetch / LLM / Workspace 时，不会执行外部命令，只展示 receipt 去重。
- 未配置 Workspace 时，不会写入真实报告，只展示研究报告写回阶段。
- 未配置模型 key 时，`demo.py` 和 `smoke.py` 仍可运行；`agentengine run/web` 是否需要模型取决于你的 Agent 逻辑。

## 常见问题

- **为什么不直接重跑任务？** 长任务往往包含付费 API、文件写入、工单提交或状态变更，重复执行会产生副作用。
- **checkpoint 应该存在哪里？** 生产建议放在持久化 session store，并按租户或应用 namespace 隔离。
- **tool receipt 和日志有什么区别？** 日志用于观察，receipt 用于恢复决策；恢复逻辑不能只依赖文本日志。
- **这个 demo 会访问真实平台吗？** 默认不会。它只使用公开 fixture，适合作为开源样例和本地教学工程。
