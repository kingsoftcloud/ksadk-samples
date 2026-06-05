# Knowledge Base RAG - DeepAgents

DeepAgents 知识库问答示例，把知识库检索和运行状态查询作为工具交给 DeepAgents 使用。

## 适用场景

- 想用 DeepAgents 做工具式 RAG。
- 想比较 DeepAgents 与 ADK、LangChain、LangGraph 的知识库写法。
- 想验证 KSADK 0.6.2 下 DeepAgents 0.6.x 与知识库工具的组合。

## 你会看到什么

- `search_knowledge_base(query)` 检索本地或云端知识库。
- `get_kb_runtime_status()` 返回当前知识库模式。
- `create_deep_agent(..., tools=[...], system_prompt=...)` 创建可调用工具的图。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写模型配置。默认本地知识库不需要云资源，但 DeepAgents 需要模型支持工具调用。

## 本地运行

```bash
cd 02-use-cases/knowledge-base-rag/deepagents
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以观察 DeepAgents 是否先调用知识库工具再回答。

## 部署

```bash
uv run agentengine deploy .
```

部署前配置云账号 AK/SK。云端知识库配置见下一节。

## 示例问题

```text
KSADK 怎么部署 Agent？
```

```text
当前知识库配置是什么？
```

## 可选云端知识库

```bash
KSADK_KB_DATASET_ID=your-dataset-id
KSADK_KB_ENDPOINT=aicp.api.ksyun.com
KSADK_KB_REGION=cn-beijing-6
KSADK_KB_SCHEME=https
```

不配置 dataset 时，示例会使用仓库内置本地文档。

## 常见问题

- DeepAgents 0.6.x 使用 `system_prompt`，不是 `instructions`。
- 如果模型没有调用 `search_knowledge_base`，尝试明确要求“请先检索知识库”。
- 如果云端知识库暂不可用，可以先用本地 corpus 验证主流程。
