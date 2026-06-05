# AgentEngine Toolsets - LangGraph

这个示例从一个内部综合验证 demo 中抽取了可开源的通用模式：在 LangGraph 中绑定 KSADK 0.6.2 的 AgentEngine 内置 toolsets，同时追加业务自定义 tool 和外层 graph node。

它适合已经跑通过 `hello-world/langgraph`、想继续了解 AgentEngine 平台能力边界的用户。

## 适用场景

- 想在 LangGraph 项目中使用 KSADK 0.6.2 的 AgentEngine 内置 toolsets。
- 想学习如何通过 dispatcher 渐进式暴露低频或高风险工具。
- 想把业务自定义工具、状态说明工具和外层 LangGraph 编排组合在一个可部署示例里。
- 想从内部综合 demo 迁移出一个不包含真实凭证、内网地址和测试 artifact 的开源版本。

## 你会学到什么

- 如何用 `get_agentengine_tools(include=[...])` 绑定 KSADK 内置工具。
- 如何用 `describe_agentengine_tools()` 在运行时解释当前工具、风险等级和启用状态。
- 如何用 `agentengine_tool_dispatcher` 渐进式发现、描述和调用低频工具。
- 如何把业务自定义 tool 与 KSADK 内置 tool 放在同一个 ReAct 子图里。
- 如何在外层 `StateGraph` 中增加路由节点、自定义上下文节点和最终整理节点。
- 如何在未配置 Skill Runtime、Workspace、Sandbox、知识库或长期记忆时给出清楚边界，而不是伪造执行结果。

## 目录结构

```text
02-use-cases/agentengine-toolsets/langgraph/
  README.md
  agent.py
  agentengine.yaml
  requirements.txt
```

`agent.py` 中有三类内容：

- KSADK 内置 toolsets：`get_agentengine_tools(include=["focused", "agentengine_tool_dispatcher"])`
- 业务自定义 tools：`graph_status`、`component_status`、`release_risk_matrix`
- LangGraph 编排：`route_turn -> prepare_custom_context -> run_specialist -> finalize_answer`

## 环境准备

在 `ksadk-samples` 仓库根目录准备虚拟环境：

```bash
uv venv
uv pip install -e ".[test]"
```

进入本示例目录并安装示例最小依赖：

```bash
cd 02-use-cases/agentengine-toolsets/langgraph
uv pip install -r requirements.txt
```

`requirements.txt` 使用本示例的最小依赖：

```text
ksadk[langgraph]
```

本示例按 KSADK 0.6.2 的公开接口编写并验证。你也可以直接在仓库根目录安装完整能力集：

```bash
uv pip install -U "ksadk[all]"
```

如果你只运行这个 LangGraph 示例，安装 `requirements.txt` 中的最小依赖即可。

## 模型配置

回到 `ksadk-samples` 仓库根目录复制环境变量模板：

```bash
cp .env.example .env
```

至少填写：

```bash
OPENAI_API_KEY=your-openai-compatible-api-key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4o-mini
```

只要你的模型服务兼容 OpenAI Chat Completions API，就可以替换 `OPENAI_API_BASE` 和 `OPENAI_MODEL_NAME`。

## 本地运行

进入示例目录：

```bash
cd 02-use-cases/agentengine-toolsets/langgraph
uv run agentengine run -i .
```

推荐先问：

```text
当前组件状态如何？有哪些工具已经绑定？
```

这个问题会触发 `component_status`，即使你没有配置 Skill Space、Workspace、Sandbox、知识库或长期记忆，也能看到清楚的能力边界。

## Web UI 调试

在示例目录运行：

```bash
uv run agentengine web .
```

浏览器打开后，可以在会话里测试：

```text
解释一下这个 LangGraph 图有哪些节点和边。
```

```text
帮我为 workspace、skill runtime、sandbox 相关改动生成发布风险矩阵。
```

```text
Skill 和 Workspace 相关工具怎么发现？先列出可用工具。
```

## 部署

部署前需要在 `.env` 中配置云账号 AK/SK，并确认当前账号有 AgentEngine 部署权限：

```bash
KSYUN_ACCESS_KEY=your-access-key
KSYUN_SECRET_KEY=your-secret-key
```

然后在示例目录执行：

```bash
uv run agentengine deploy .
```

部署后建议用同一组示例问题做 smoke test，确认本地 Web UI 与部署环境的工具绑定和模型调用行为一致。

## 示例问题

### 组件状态

```text
当前组件状态如何？哪些能力需要额外配置？
```

预期路径：调用 `component_status`，说明已绑定的 focused tools、dispatcher、自定义 tools，以及 Skill Runtime / Workspace / Sandbox / Platform 能力边界。

### LangGraph 结构

```text
这个示例的 LangGraph 图是怎么串起来的？
```

预期路径：调用 `graph_status`，返回节点、边、KSADK toolset 绑定方式和扩展点。

### 发布风险矩阵

```text
我要发布一个改动，涉及 workspace、skill runtime、sandbox，请生成风险矩阵。
```

预期路径：调用 `release_risk_matrix`，生成结构化风险、验证建议和下一步。

### 渐进式工具发现

```text
请用 dispatcher 看看 Workspace 还有哪些可调用工具。
```

预期路径：调用 `agentengine_tool_dispatcher` 的 `list` 或 `describe`。如果你继续要求写文件、删文件或执行命令，高风险工具可能由 KSADK Tool Gateway 返回 `approval_required`。

## 可选配置

本示例默认不要求配置以下能力。你可以后续按需打开。

### Skill Space

配置后，`list_skills`、`search_skills`、`load_skill` 可以发现并加载 Skill 指令：

```bash
KSADK_SKILL_SPACE_IDS=your-skill-space-id
```

`execute_skills` 需要额外配置 Skill Runtime 或 Sandbox 后端。本示例不会默认执行隔离任务。

### Workspace

在 AgentEngine Web UI 或 Hosted UI 中运行时，Workspace 工具只会操作 UI 提供的 workspace 目录。不要把它当作宿主机 shell 或任意文件系统访问入口。

### Sandbox

`run_command` 和 `run_code` 只通过已配置的隔离 sandbox backend 执行。未配置时，示例应解释缺少配置，而不是模拟命令结果。

### 知识库和长期记忆

如果你的环境安装并配置了 KSADK 知识库或长期记忆能力，`get_agentengine_tools()` 的 platform toolset 会按当前环境自动暴露相关工具。未配置时，本示例仍可运行，并通过 `component_status` 说明当前状态。

## 脱敏说明

本示例只保留通用工程模式，不包含内部 demo 的真实配置：

- 不包含真实 AK/SK、API key、token 或账号 ID。
- 不包含内网 endpoint、沙箱 region 域名、DNS override IP 或已有 sandbox ID。
- 不包含具体 Skill Space ID、Skill Runtime template ID、测试 artifact 或 Playwright 日志。
- 不提交 `.env`、`.agentengine/`、`.playwright-cli/`、`__pycache__/` 或 `.pytest_cache/`。

如果你从自己的项目迁移类似示例，提交前请至少搜索：

```bash
rg -n "AK|SK|SECRET|TOKEN|KEY|PASSWORD|http://|https://|[0-9]{1,3}(\\.[0-9]{1,3}){3}" .
```

确认所有真实凭证、内部地址和用户数据都已移除或替换为占位符。

## 常见问题

### 为什么不直接绑定全部 KSADK 工具？

全部绑定会增加模型上下文体积，也会让用户更难理解工具边界。本示例默认绑定 `focused` 和 `agentengine_tool_dispatcher`：常用低风险能力直接可见，低频或高风险能力通过 dispatcher 按需发现。

### 为什么示例里重写了 `component_status`？

KSADK 0.6.2 自带 `component_status`。本示例为了展示“业务项目可以替换或增强平台状态说明”，过滤掉内置同名工具，再绑定一个更贴合本示例的自定义 `component_status`。真实项目也可以选择直接使用内置版本。

### 没有配置 Skill Space 或 Sandbox 时能运行吗？

能运行。未配置时，相关工具会返回未启用或缺少配置的状态；模型仍可回答普通问题，也可以通过 `graph_status` 和 `component_status` 解释当前边界。

### 本示例和 `tool-calling/langgraph` 有什么区别？

`tool-calling/langgraph` 展示最小自定义工具调用；本示例展示 AgentEngine 场景下的 KSADK 内置 toolsets、dispatcher、业务自定义工具和外层 LangGraph 编排，属于进阶用例。

### 这个示例适合改成生产项目吗？

可以作为起点，但生产项目通常需要补充鉴权、观测、错误分类、回归测试、审批策略和部署环境隔离。建议先保留 `component_status` 这类状态工具，方便定位配置问题。
