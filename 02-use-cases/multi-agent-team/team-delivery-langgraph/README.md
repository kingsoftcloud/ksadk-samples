# 多 Agent 团队（协作交付）- LangGraph

演示 Multi-Agent Team 如何把复杂任务拆成角色分工、并行轨迹、冲突合并和验收清单。这是一个多文件 LangGraph Agent 工程，不是单文件脚本；默认使用本地公开 fixture，所以 clone 后不启动真实子 Agent 也能看到完整协作流程。

## 适用场景

- 想学习多 Agent 团队如何拆分 Planner、Researcher、Builder、Reviewer。
- 想演示长任务中如何收集并行产物、合并冲突并给出验收标准。
- 想把 fixture 替换为真实子 Agent、任务队列或协作日志。

## 工程结构

| 文件 | 作用 |
| --- | --- |
| `agent.py` | LangGraph `root_agent` 入口。 |
| `tools.py` | 角色分工、并行轨迹、冲突合并和验收清单渲染。 |
| `data.py` | 本地公开团队协作 fixture，可替换为真实任务队列。 |
| `prompts.py` | 多智能体协调者角色和输出约束。 |
| `demo.py` | 离线演示脚本，不需要模型 key。 |
| `workflow.py` | LangGraph 编排：角色分工、并行轨迹、冲突合并、验收清单。 |

## 你会看到什么

- `角色分工`：Planner、Researcher、Builder、Reviewer 的职责和产物。
- `并行轨迹`：每个角色当前任务和状态。
- `冲突合并`：处理速度、质量、README 和代码行为冲突的规则。
- `验收清单`：交付前必须完成的门禁。

## 环境准备

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
```

真实模型调用需要 `.env`：

```bash
OPENAI_API_KEY=your-openai-compatible-api-key
OPENAI_MODEL_NAME=gpt-4o-mini
```

## 本地运行

```bash
cd 02-use-cases/multi-agent-team/team-delivery-langgraph
cp ../../../.env.example .env
uv pip install -r requirements.txt
uv run agentengine run -i .
```

快速看离线输出：

```bash
uv run python demo.py
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以观察 Agent 如何输出角色分工、并行轨迹、冲突合并和验收清单。未接入真实子 Agent 时，输出会明确标注为 fixture。

## 部署

```bash
uv run agentengine deploy .
```

部署前请确认子 Agent 服务、任务队列和权限边界已经配置；未配置时样例只展示本地 fixture 的协作流程。

## 示例问题

- `组织一个团队把 samples 仓库补齐。`
- `让多个角色评估 0.6.4 发布后的下一阶段路线。`

## 接入真实能力

- 子 Agent：把 `assign_team_roles` 替换为真实 Agent 注册表。
- 任务队列：把 `collect_parallel_progress` 替换为队列状态查询。
- Workspace：把每个角色产物写成会话文件并汇总。
- Reviewer：把 public-preflight、截图和 smoke 结果写入验收清单。

## 常见问题

- 如果运行时报依赖缺失，请确认已安装 `ksadk[all]` 或当前框架 extra。
- 如果没有真实子 Agent，样例不会启动外部任务，只展示公开 fixture 的协作流程。
- 如果你的团队角色不同，请先修改 `TEAM_ROLES` 和 `PARALLEL_TASKS`。
- 如果要开源，请确认协作日志不包含真实客户、账号、token 或内部项目排期。
