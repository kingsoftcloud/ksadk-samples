# KSADK Samples

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/kingsoftcloud/ksadk-python)

KSADK Samples 是面向 AgentEngine / KSADK 的官方场景化代码工坊。仓库里的 `Samples` 和 `Examples` 含义一致：都指可运行、可部署、可对比框架写法的公开样例。

## 场景导航

### 按场景选择

| 你想做什么 | 推荐样例 | 覆盖框架 | 说明 |
| --- | --- | --- | --- |
| 先确认 SDK、模型和部署链路能跑通 | `01-tutorials/hello-world` | ADK / LangGraph / LangChain / DeepAgents | 最小对话 Agent |
| 学自定义工具调用 | `01-tutorials/tool-calling` | ADK / LangGraph / LangChain / DeepAgents | 绑定本地业务 tool，并通过 AgentEngine 运行 |
| 学短期记忆和长期记忆接入思路 | `01-tutorials/memory` | ADK / LangGraph / LangChain / DeepAgents | 默认本地记忆，可扩展到平台长期记忆 |
| 做知识库问答 | `02-use-cases/knowledge-base-rag` | ADK / LangGraph / LangChain / DeepAgents | 默认本地 corpus，可选接入金山云知识库 |
| 做平台能力综合验证 | `02-use-cases/agentengine-toolsets/langgraph` | LangGraph | KSADK 内置 toolsets、dispatcher、Skill Space、Workspace、Sandbox、知识库、长期记忆配置边界 |

### 推荐主推 Demo

KsADK 0.6.3 开源发布建议优先展示：

```bash
cd 02-use-cases/agentengine-toolsets/langgraph
uv pip install -r requirements.txt
uv run agentengine run -i .
```

这个 demo 展示 LangGraph 如何绑定 AgentEngine Toolsets，并重点覆盖 Skill Space 的 `list_skills`、`search_skills`、`load_skill` 设计。未配置 Skill Space、Skill Runtime、Workspace、Sandbox、知识库或长期记忆时，demo 会解释缺失配置和降级行为，不会伪造平台结果。

## 环境准备

在仓库根目录准备虚拟环境：

```bash
uv venv
uv pip install -e ".[test]"
cp .env.example .env
```

只运行单个样例时，进入样例目录后安装它自己的最小依赖：

```bash
cd 01-tutorials/hello-world/adk
uv pip install -r requirements.txt
```

也可以一次性安装完整能力集：

```bash
uv pip install -U "ksadk[all]"
```

编辑 `.env`，至少配置 OpenAI 兼容模型：

```bash
OPENAI_API_KEY=your-openai-compatible-api-key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4o-mini
```

## 平台能力配置速查

这些变量只在对应场景需要时填写。只配置模型时，大多数基础 Samples / Examples 仍可运行。

| 能力 | 关键环境变量 | 含义 | 未配置时降级 |
| --- | --- | --- | --- |
| 云账号 | `KSYUN_ACCESS_KEY`、`KSYUN_SECRET_KEY`、`KSYUN_REGION` | 部署 Agent、调用金山云知识库、Skill Service、长期记忆 SDK 后端时使用 | 不能部署或调用云服务，本地基础样例不受影响 |
| Skill Space | `KSADK_SKILL_SPACE_IDS` 或 `SKILL_SPACE_ID`、`KSADK_PUBLIC_SKILL_SPACE_IDS`、`KSADK_SKILL_SERVICE_URL` 或 `KSADK_SKILL_SERVICE_ENDPOINT`、`KSADK_SKILL_SERVICE_ACCESS_KEY`、`KSADK_SKILL_SERVICE_SECRET_KEY` | 发现、搜索、加载 Skill 指令 | `list_skills` / `search_skills` / `load_skill` 返回缺少 Space ID、endpoint 或凭证 |
| Skill Runtime | `KSADK_SKILL_RUNTIME_BACKEND`、`KSADK_SKILL_RUNTIME_AGENT_PATH`、`KSADK_SKILL_RUNTIME_TEMPLATE_ID`、`KSADK_SKILL_RUNTIME_TIMEOUT`、`E2B_API_KEY` | 执行 Skill workflow；`local_process` 用于本地调试，`e2b` 用于隔离运行 | 仍可发现和加载 Skill，但 `execute_skills` 不执行 workflow |
| Workspace | 本地 `agentengine run/web` 通常由会话自动注入；远端由 AgentEngine runtime 注入 | 读写当前会话 workspace 文件 | 只能说明 workspace 不可用或为空，不能访问宿主机任意路径 |
| Sandbox | `KSADK_SANDBOX_BACKEND=e2b`、`KSADK_SANDBOX_TEMPLATE_ID`、`KSADK_SANDBOX_TIMEOUT`、`KSADK_SANDBOX_ALLOW_INTERNET_ACCESS`、`E2B_API_KEY` | 隔离执行命令或代码 | `run_command` / `run_code` 返回未配置或不可用 |
| 知识库 | `KSADK_KB_DATASET_ID`、`KSADK_KB_ENDPOINT`、`KSADK_KB_REGION`、`KSADK_KB_TOP_K`、`KSADK_KB_ACCESS_KEY`、`KSADK_KB_SECRET_KEY` | 检索金山云知识库 | RAG demo 使用本地 corpus；平台 toolset 不伪造云检索答案 |
| 长期记忆 | `KSADK_LTM_BACKEND`、`KSADK_LTM_INDEX`、`KSADK_LTM_NAMESPACE`、`KSADK_LTM_HTTP_URL`、`KSADK_LTM_ENDPOINT` | 跨会话保存和检索用户记忆 | 记忆 demo 使用本地示例记忆；平台长期记忆工具不加载历史记忆 |

完整变量说明见主推 demo：[02-use-cases/agentengine-toolsets/langgraph/README.md](02-use-cases/agentengine-toolsets/langgraph/README.md)。

## 运行样例

进入任意样例目录：

```bash
cd 01-tutorials/hello-world/adk
uv run agentengine run -i .
uv run agentengine web .
```

需要部署时，先填写云账号：

```bash
KSYUN_ACCESS_KEY=your-access-key
KSYUN_SECRET_KEY=your-secret-key
```

然后运行：

```bash
uv run agentengine deploy .
```

每个样例目录都有自己的 `README.md`、`agent.py`、`agentengine.yaml` 和 `requirements.txt`。

## 相关资源

- 文档：https://kingsoftcloud.github.io/ksadk-python/
- KSADK 仓库：https://github.com/kingsoftcloud/ksadk-python
- Wiki：https://zread.ai/kingsoftcloud/ksadk-python
- Web UI 仓库：https://github.com/kingsoftcloud/ksadk-web
- PyPI：https://pypi.org/project/ksadk/
- 开源协议：Apache-2.0

## 仓库校验

```bash
uv run python scripts/validate_samples.py
uv run pytest -q
```

公开同步或发布前运行：

```bash
make public-preflight
```

`validate_samples.py` 会检查样例结构、README 首页索引、样例 README 必备章节、Python 语法 smoke 和敏感内容扫描。`public-preflight` 还会单独执行公开安全扫描，作为发布前双保险。

## 后续计划

- 补充更多真实业务场景的 use case，但只在可以本地运行、可部署、可脱敏验证后加入代码目录。
- 为 Skill Runtime 和 Sandbox 增加更细粒度的 E2E 说明，前提是不提交真实 template ID、内部 endpoint 或测试 artifact。

## 目录结构

```text
01-tutorials/
  hello-world/
  tool-calling/
  memory/
02-use-cases/
  knowledge-base-rag/
  agentengine-toolsets/
common/
scripts/
template/
tests/
```
