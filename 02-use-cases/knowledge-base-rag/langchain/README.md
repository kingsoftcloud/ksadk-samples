# Knowledge Base RAG - LangChain

LangChain 知识库问答示例，在 `ksadk_prepare_input` 中检索知识库并把上下文注入 Prompt。

## 适用场景

- 想用 LangChain Runnable 实现简单 RAG。
- 想了解平台知识库上下文和本地检索结果如何合并。
- 想先用仓库内置文档跑通，再接入云端知识库。

## 你会看到什么

- `ksadk_prepare_input` 从 `payload["input"]` 读取问题。
- 函数会合并 `session_context["kb_context"]` 和 `search_knowledge(query)` 的结果。
- `root_agent` 使用 Prompt、模型和 `StrOutputParser` 生成最终回答。

## 环境准备

在仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写 `.env` 中的模型配置。默认本地知识库不需要 AK/SK。

## 本地运行

```bash
cd 02-use-cases/knowledge-base-rag/langchain
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中适合检查模型回答是否基于知识库上下文。

## 部署

```bash
uv run agentengine deploy .
```

部署前配置云账号 AK/SK。使用云端知识库时同时配置 dataset。

## 示例问题

```text
KSADK 怎么部署 Agent？
```

```text
知识库示例默认读哪些文档？
```

## 可选云端知识库

```bash
KSADK_KB_DATASET_ID=your-dataset-id
KSADK_KB_ENDPOINT=aicp.api.ksyun.com
KSADK_KB_REGION=cn-beijing-6
KSADK_KB_SCHEME=https
```

保持 `KSADK_KB_DATASET_ID` 为空时，示例会使用本地 corpus。

## 常见问题

- LangChain 示例把检索放在输入准备阶段，适合最小 RAG；复杂检索链可拆成 Runnable。
- 如果云端知识库不可用，先确认本地 corpus 路径仍存在。
- 如果要调试检索结果，可临时打印 `search_knowledge(query)` 返回值。
