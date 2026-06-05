# KSADK Samples

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/kingsoftcloud/ksadk-python)

KSADK Samples 是面向 AgentEngine / KSADK 的官方代码工坊。仓库提供可直接运行、可部署、可对比不同框架写法的 Agent 示例。

## 相关资源

- 文档：https://kingsoftcloud.github.io/ksadk-python/
- KSADK 仓库：https://github.com/kingsoftcloud/ksadk-python
- Wiki：https://zread.ai/kingsoftcloud/ksadk-python
- Web UI 仓库：https://github.com/kingsoftcloud/ksadk-web
- PyPI：https://pypi.org/project/ksadk/
- 开源协议：Apache-2.0

首版覆盖四类能力：

| 示例 | 难度 | 覆盖框架 | 说明 |
| --- | --- | --- | --- |
| `01-tutorials/hello-world` | 入门 | ADK / LangGraph / LangChain / DeepAgents | 最小对话 Agent |
| `01-tutorials/tool-calling` | 入门 | ADK / LangGraph / LangChain / DeepAgents | 自定义工具调用 |
| `01-tutorials/memory` | 普通 | ADK / LangGraph / LangChain / DeepAgents | 本地记忆与平台长期记忆接入思路 |
| `02-use-cases/knowledge-base-rag` | 进阶 | ADK / LangGraph / LangChain / DeepAgents | 本地知识库 + 可选金山云知识库 |
| `02-use-cases/agentengine-toolsets/langgraph` | 进阶 | LangGraph | KSADK 内置 toolsets + dispatcher + 自定义业务工具 |

## 环境准备

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

本仓库的本地 smoke / e2e 统一使用 `uv run ...`。新用户可以直接安装 `ksadk[all]` 覆盖全部示例能力；每个样例目录的 `requirements.txt` 保留该样例的最小依赖声明，方便只运行单个示例时按需安装。

编辑 `.env`，至少配置模型：

```bash
OPENAI_API_KEY=...
OPENAI_API_BASE=...
OPENAI_MODEL_NAME=...
```

如果需要部署或连接金山云知识库，再配置：

```bash
KSYUN_ACCESS_KEY=...
KSYUN_SECRET_KEY=...
KSADK_KB_DATASET_ID=...
KSADK_KB_ENDPOINT=aicp.api.ksyun.com
KSADK_KB_REGION=cn-beijing-6
```

## 运行样例

进入任意样例目录：

```bash
cd 01-tutorials/hello-world/adk
uv pip install -r requirements.txt
uv run agentengine run -i .
uv run agentengine web .
uv run agentengine deploy .
```

每个样例目录都有自己的 `README.md`、`agent.py`、`agentengine.yaml` 和 `requirements.txt`。

## 仓库校验

```bash
uv run python scripts/validate_samples.py
uv run pytest -q
```

公开同步或发布前运行：

```bash
make public-preflight
```

该目标会执行公开安全扫描、样例结构校验和测试。`ksadk-samples` 目前不需要复制 `ksadk-python` 的长期公开工作树流程；如果未来同一个仓库同时承载内部样例和公开样例，再引入公开候选分支和工作树。

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
