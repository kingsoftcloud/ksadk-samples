# 知识助手（Knowledge Base RAG）- LangGraph

LangGraph 知识库问答示例，用单节点图演示如何在节点中检索知识库并生成回答。

## 适用场景

- 想在 LangGraph 中控制 RAG 流程。
- 想了解如何把平台知识库上下文放入图状态。
- 想从单节点 RAG 继续扩展为多节点检索、重排、回答图。

## 你会看到什么

- `AgentState` 保存 `query`、`kb_context` 和 `answer`。
- `ksadk_prepare_state` 读取用户问题和可选平台知识库上下文。
- `answer` 节点根据问题选择读取运行状态或检索知识库。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写模型配置。默认走仓库本地知识库。

## 本地运行

```bash
cd 02-use-cases/knowledge-base-rag/langgraph
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以观察不同问题是否进入“配置状态”或“知识库检索”路径。

## 部署

```bash
uv run agentengine deploy .
```

部署前配置云账号 AK/SK。云端知识库是可选能力。

## 示例问题

```text
KSADK 怎么部署 Agent？
```

```text
当前知识库配置状态是什么？
```

## 可选云端知识库

```bash
KSADK_KB_DATASET_ID=your-dataset-id
KSADK_KB_ENDPOINT=aicp.api.ksyun.com
KSADK_KB_REGION=cn-beijing-6
KSADK_KB_SCHEME=https
```

未配置 dataset 时，`search_knowledge()` 会回退到 `common/corpus/`。

## 常见问题

- 如果想增加检索前重写查询，可以在 `answer` 前新增一个 LangGraph 节点。
- 如果想增加来源校验，可以把检索结果拆成结构化状态字段。
- 如果云端知识库失败，本地 corpus 仍可用于验证样例主流程。
