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

本示例不强制配置 Skill Runtime、Workspace、Sandbox、知识库或长期记忆。只配置模型时，示例可以正常回答普通问题，也可以用 `component_status` 解释哪些平台能力尚未启用。

需要接入平台能力时，建议先按下面顺序配置：先配置模型和云账号，再配置 Skill Space / 知识库 / 长期记忆这类数据来源，最后再打开会执行代码或写文件的 Skill Runtime、Workspace、Sandbox。

### 配置速查表

| 能力 | 最小配置 | 主要工具 | 没配置时的表现 |
| --- | --- | --- | --- |
| Skill Space | `KSADK_SKILL_SPACE_IDS` 或 `SKILL_SPACE_ID` | `list_skills`、`search_skills`、`load_skill` | 无法发现用户 Skill |
| Skill Runtime | `KSADK_SKILL_RUNTIME_BACKEND`，需要执行隔离任务时再配 template | `execute_skills` | 只解释缺少运行后端，不执行 Skill workflow |
| Workspace | 本地运行不需要额外变量；部署后由 AgentEngine 会话提供 workspace | `workspace_status`、`list_workspace_files`、`read_workspace_file` | 只能访问当前会话 workspace，不能访问任意宿主机路径 |
| Sandbox | `KSADK_SANDBOX_BACKEND=e2b` + `KSADK_SANDBOX_TEMPLATE_ID` | `sandbox_status`、`run_command`、`run_code` | 命令执行类工具返回未配置或不可用 |
| 知识库 | `KSADK_KB_DATASET_ID` + 云账号 AK/SK | `search_knowledge_base` | 不暴露或无法完成云知识库检索 |
| 长期记忆 | `KSADK_LTM_BACKEND`，云端模式还需要 namespace 或 HTTP URL | `load_memory`、`save_memory` | 不加载历史长期记忆 |

### 通用云账号

部署 Agent 或调用金山云平台服务时通常需要云账号凭证：

```bash
KSYUN_ACCESS_KEY=your-access-key
KSYUN_SECRET_KEY=your-secret-key
KSYUN_ACCOUNT_ID=your-account-id
KSYUN_REGION=cn-beijing-6
```

变量含义：

| 变量 | 含义 | 是否必填 |
| --- | --- | --- |
| `KSYUN_ACCESS_KEY` | 金山云访问密钥 ID。知识库、Skill Service、长期记忆 SDK 后端都可以复用它。 | 部署或调用云服务时必填 |
| `KSYUN_SECRET_KEY` | 金山云访问密钥 Secret。不要提交到 Git。 | 部署或调用云服务时必填 |
| `KSYUN_ACCOUNT_ID` | 金山云账号 ID。部分 Skill Service 请求会透传到 `X-Ksc-Account-Id`。 | 按平台要求填写 |
| `KSYUN_REGION` | 默认区域。未单独配置能力区域时会作为 fallback。 | 可选，默认 `cn-beijing-6` |

### Skill Space

Skill Space 用于发现和下载 Skill 指令。配置后，`list_skills`、`search_skills`、`load_skill` 才能看到你的 Skill。

最小配置：

```bash
KSADK_SKILL_SPACE_IDS=your-skill-space-id
KSADK_PUBLIC_SKILL_SPACE_IDS=
KSYUN_ACCESS_KEY=your-access-key
KSYUN_SECRET_KEY=your-secret-key
```

也可以用兼容变量：

```bash
SKILL_SPACE_ID=your-skill-space-id
```

Skill Service 连接变量：

| 变量 | 含义 |
| --- | --- |
| `KSADK_SKILL_SPACE_IDS` | 用户 Skill Space ID，多个 ID 用英文逗号分隔。优先级高于 `SKILL_SPACE_ID`。 |
| `SKILL_SPACE_ID` | 单个 Skill Space ID 的兼容写法。 |
| `KSADK_PUBLIC_SKILL_SPACE_IDS` | 公共 Skill Space ID，多个 ID 用英文逗号分隔。 |
| `KSADK_SKILL_SERVICE_URL` | 完整 Skill Service 地址。设置后优先使用它。 |
| `KSADK_SKILL_SERVICE_ENDPOINT` | Skill Service endpoint。未设置 `KSADK_SKILL_SERVICE_URL` 时使用。 |
| `KSADK_SKILL_SERVICE_SCHEME` | endpoint scheme，常用值为 `https`。 |
| `KSADK_SKILL_SERVICE_ACCESS_KEY` | Skill Service 专用 AK；未设置时 fallback 到 `KSYUN_ACCESS_KEY` 或 `KS3_ACCESS_KEY`。 |
| `KSADK_SKILL_SERVICE_SECRET_KEY` | Skill Service 专用 SK；未设置时 fallback 到 `KSYUN_SECRET_KEY` 或 `KS3_SECRET_KEY`。 |
| `KSADK_SKILL_SERVICE_ACCOUNT_ID` | Skill Service 专用账号 ID；未设置时 fallback 到 `KSYUN_ACCOUNT_ID`。 |
| `KSADK_SKILL_SERVICE_REGION` | Skill Service 区域；未设置时 fallback 到 `KSYUN_REGION`，再 fallback 到 `cn-beijing-6`。 |
| `KSADK_SKILL_SERVICE_API_VERSION` | Skill Service API 版本，默认 `2024-06-12`。 |
| `KSADK_SKILL_SERVICE_SIGN_SERVICE` | 请求签名服务名，默认 `aicp`。 |

验证方式：

```text
请用 agentengine_tool_dispatcher 列出 skill 相关工具，再搜索我当前 Skill Space 里有哪些 Skill。
```

如果配置正确，模型会通过 dispatcher 找到 `list_skills`、`search_skills` 或 `load_skill`。如果缺少凭证或 Space ID，返回里会出现明确的错误原因。

### Skill Runtime

Skill Runtime 负责运行 `execute_skills` 发起的 Skill workflow。只发现和读取 Skill 不一定需要 Runtime；真正执行 workflow 时才需要。

本地进程模式适合开发调试：

```bash
KSADK_SKILL_RUNTIME_BACKEND=local_process
KSADK_SKILL_RUNTIME_AGENT_PATH=/absolute/path/to/skill-runtime-agent.py
KSADK_SKILL_RUNTIME_TIMEOUT=900
```

隔离沙箱模式适合执行更高风险的 Skill workflow：

```bash
KSADK_SKILL_RUNTIME_BACKEND=e2b
KSADK_SKILL_RUNTIME_TEMPLATE_ID=your-runtime-template-id
KSADK_SKILL_RUNTIME_TIMEOUT=900
KSADK_SKILL_RUNTIME_ALLOW_INTERNET_ACCESS=true
E2B_API_KEY=your-e2b-api-key
```

变量含义：

| 变量 | 含义 |
| --- | --- |
| `KSADK_SKILL_RUNTIME_BACKEND` | Runtime 后端。`disabled` / `none` / `off` 表示关闭；`local_process` 表示本地子进程；`e2b` 表示 E2B 沙箱。 |
| `KSADK_SKILL_RUNTIME_AGENT_PATH` | `local_process` 模式下要执行的 runtime agent 文件路径。 |
| `KSADK_SKILL_RUNTIME_TEMPLATE_ID` | E2B runtime template ID；也可用 `KSADK_SANDBOX_TEMPLATE_ID` 复用同一个 template。 |
| `KSADK_SKILL_RUNTIME_TIMEOUT` | Skill workflow 超时时间，单位秒，默认 `900`。 |
| `KSADK_SKILL_RUNTIME_ALLOW_INTERNET_ACCESS` | E2B runtime 是否允许访问互联网，默认 `true`。 |
| `E2B_API_KEY` | E2B SDK 使用的认证密钥。KSADK 透传给 `e2b` 包，不会在日志里明文展示。 |

验证方式：

```text
请先说明 execute_skills 当前是否可用；如果可用，运行一个只读取 Skill 指令、不访问外部网络的最小 workflow。
```

生产环境建议先让模型解释将要执行的 Skill、输入文件和预期输出，再让审批策略决定是否继续。

### Workspace

Workspace 是 AgentEngine 会话的文件工作区。它不是宿主机任意路径访问入口，也不是 shell。Workspace 工具只能操作当前 session workspace root 下面的文件。

常用工具：

| 工具 | 用途 | 风险级别 |
| --- | --- | --- |
| `workspace_status` | 查看 workspace root 和最近文件。 | 低 |
| `list_workspace_files` | 列出 workspace 目录。 | 低 |
| `read_workspace_file` | 读取 UTF-8 文本文件。 | 低 |
| `write_workspace_file`、`write_workspace_files` | 写入一个或多个文件。 | 中 |
| `edit_workspace_file` | 用精确片段替换编辑文件。 | 中 |
| `lint_workspace_file` | 对文本文件做轻量检查。 | 低 |
| `search_workspace_files` | 在 workspace 内搜索文本。 | 低 |
| `delete_workspace_file` | 删除 workspace 文件或空目录。 | 高 |

本地运行时一般不需要额外配置。部署或 Hosted UI 场景下，workspace 由 AgentEngine runtime 和会话注入。调试 CLI 远端 workspace 文件时，通常还会用到 `agentengine files` 命令，但这个示例本身不依赖它。

验证方式：

```text
请调用 workspace_status，然后列出 workspace 根目录文件。不要写文件。
```

如果你要测试写入能力，可以让模型先写一个小文件，再读回验证：

```text
请在 workspace 写入 demo/hello.txt，内容是 hello ksadk，然后读回文件确认。
```

### Sandbox

Sandbox 用于隔离执行命令或代码。`run_command` 和 `run_code` 不会直接在你的宿主机上执行；它们依赖已配置的 sandbox backend。

E2B 最小配置：

```bash
KSADK_SANDBOX_BACKEND=e2b
KSADK_SANDBOX_TEMPLATE_ID=your-sandbox-template-id
KSADK_SANDBOX_TIMEOUT=900
KSADK_SANDBOX_ALLOW_INTERNET_ACCESS=true
KSADK_SANDBOX_TYPE=aio
E2B_API_KEY=your-e2b-api-key
```

变量含义：

| 变量 | 含义 |
| --- | --- |
| `KSADK_SANDBOX_BACKEND` | Sandbox 后端。KSADK 0.6.2 支持 `e2b`；`none` / `disabled` / `off` 表示关闭。 |
| `KSADK_SANDBOX_TEMPLATE_ID` | E2B sandbox template ID。也会被 Skill Runtime 作为兼容 template 使用。 |
| `KSADK_SANDBOX_TIMEOUT` | 命令执行超时时间，单位秒，默认 `900`。 |
| `KSADK_SANDBOX_ALLOW_INTERNET_ACCESS` | 是否允许 sandbox 访问互联网，默认 `true`。 |
| `KSADK_SANDBOX_TYPE` | Sandbox 类型，默认 `aio`。 |
| `E2B_API_KEY` | E2B SDK 使用的认证密钥。 |

验证方式：

```text
请先调用 sandbox_status，说明 sandbox 后端是否启用。启用后再运行 python -V。
```

不要把 sandbox 当成长期存储。每次会话创建的 sandbox 可能是临时环境，输出文件需要通过 workspace 或平台 artifact 明确保存。

### 知识库

知识库工具用于检索金山云知识库。配置 `KSADK_KB_DATASET_ID` 后，`get_agentengine_tools()` 的 platform toolset 会尝试暴露 `search_knowledge_base`。

最小配置：

```bash
KSADK_KB_DATASET_ID=your-dataset-id
KSADK_KB_ENDPOINT=aicp.api.ksyun.com
KSADK_KB_REGION=cn-beijing-6
KSADK_KB_SCHEME=https
KSYUN_ACCESS_KEY=your-access-key
KSYUN_SECRET_KEY=your-secret-key
```

可选检索参数：

```bash
KSADK_KB_TOP_K=5
KSADK_KB_SEARCH_METHOD=intelligence_search
KSADK_KB_SCORE_THRESHOLD=
KSADK_KB_RERANKING_ENABLE=false
```

变量含义：

| 变量 | 含义 |
| --- | --- |
| `KSADK_KB_DATASET_ID` | 知识库 Dataset ID。存在即表示启用云知识库。 |
| `KSADK_KB_ACCESS_KEY` | 知识库专用 AK；未设置时 fallback 到 `KSYUN_ACCESS_KEY`。 |
| `KSADK_KB_SECRET_KEY` | 知识库专用 SK；未设置时 fallback 到 `KSYUN_SECRET_KEY`。 |
| `KSADK_KB_ENDPOINT` | 知识库 API endpoint，公开环境可用 `aicp.api.ksyun.com`。 |
| `KSADK_KB_REGION` | 知识库区域，默认 `cn-beijing-6`。 |
| `KSADK_KB_SCHEME` | 请求协议，默认 `https`。 |
| `KSADK_KB_TOP_K` | 返回片段数量，默认 `5`。 |
| `KSADK_KB_SEARCH_METHOD` | 检索方式，默认 `intelligence_search`。 |
| `KSADK_KB_SCORE_THRESHOLD` | 分数阈值；留空表示不启用阈值过滤。 |
| `KSADK_KB_RERANKING_ENABLE` | 是否启用重排序，`true` / `false`。 |

验证方式：

```text
请用 agentengine_tool_dispatcher 查找知识库工具，然后检索“你的测试问题”。
```

如果 `KSADK_KB_DATASET_ID` 为空，本示例仍可运行，但不会伪造知识库答案。

### 长期记忆

长期记忆工具用于跨会话保存和检索用户相关信息。配置后，platform toolset 会根据当前运行上下文暴露 `load_memory`、`save_memory`。

本地后端适合开发验证：

```bash
KSADK_LTM_BACKEND=local
KSADK_LTM_INDEX=ksadk_samples
KSADK_LTM_TOP_K=5
KSADK_LTM_APP_NAME=agentengine-toolsets-langgraph
```

HTTP 后端适合对接自有服务：

```bash
KSADK_LTM_BACKEND=http
KSADK_LTM_HTTP_URL=https://your-memory-service.example.com
KSADK_LTM_HTTP_TOKEN=<token>
KSADK_LTM_INDEX=ksadk_samples
```

SDK 后端适合接入金山云长期记忆服务：

```bash
KSADK_LTM_BACKEND=sdk
KSADK_LTM_NAMESPACE=your-namespace
KSADK_LTM_AGENT_ID=your-agent-id
KSADK_LTM_SCENE_ID=_sys_general
KSADK_LTM_ENDPOINT=aicp.api.ksyun.com
KSADK_LTM_REGION=cn-beijing-6
KSADK_LTM_SCHEME=https
KSYUN_ACCESS_KEY=your-access-key
KSYUN_SECRET_KEY=your-secret-key
```

变量含义：

| 变量 | 含义 |
| --- | --- |
| `KSADK_LTM_BACKEND` | 长期记忆后端。常用值：`local`、`http`、`sdk`。留空表示不启用平台长期记忆工具。 |
| `KSADK_LTM_INDEX` | 记忆索引名。未设置时使用 app name 或默认索引。 |
| `KSADK_LTM_TOP_K` | 检索返回条数，默认 `5`。 |
| `KSADK_LTM_APP_NAME` | 应用名，用于区分不同 Agent 的记忆空间。 |
| `KSADK_LTM_HTTP_URL` | HTTP 后端服务地址。 |
| `KSADK_LTM_HTTP_TOKEN` | HTTP 后端鉴权 token。 |
| `KSADK_LTM_ACCESS_KEY` | SDK 后端专用 AK；未设置时 fallback 到 `KSYUN_ACCESS_KEY`。 |
| `KSADK_LTM_SECRET_KEY` | SDK 后端专用 SK；未设置时 fallback 到 `KSYUN_SECRET_KEY`。 |
| `KSADK_LTM_ENDPOINT` | SDK 后端 endpoint，公开环境可用 `aicp.api.ksyun.com`。 |
| `KSADK_LTM_REGION` | SDK 后端区域，默认 `cn-beijing-6`。 |
| `KSADK_LTM_SCHEME` | SDK 后端请求协议，默认 `https`。 |
| `KSADK_LTM_NAMESPACE` | 云端长期记忆 namespace。 |
| `KSADK_LTM_AGENT_ID` | 云端长期记忆所属 Agent ID。 |
| `KSADK_LTM_SCENE_ID` | 云端长期记忆场景 ID，默认 `_sys_general`。 |

验证方式：

```text
请保存一条长期记忆：我喜欢中文 README。然后检索“README 偏好”。
```

长期记忆工具依赖运行上下文里的用户 ID。没有用户上下文时，工具可能会提示缺少 invocation context，这是正常的配置边界，不代表示例代码坏了。

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
