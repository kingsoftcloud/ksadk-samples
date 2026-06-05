# Knowledge Base RAG - ADK

ADK 知识库问答示例，默认使用仓库内置本地知识库；配置云端知识库后，会优先调用真实金山云知识库。

## 适用场景

- 想用 ADK Agent 做最小 RAG 问答。
- 想先用本地文档跑通流程，再接入云端知识库。
- 想了解工具函数如何把检索结果交给 Agent 组织回答。

## 你会看到什么

- `search_knowledge_base(query)` 检索本地或云端知识库。
- `get_kb_runtime_status()` 返回当前知识库模式和有效配置。
- `root_agent` 是 ADK Agent，通过工具调用完成检索增强回答。

## 环境准备

在 `ksadk-samples` 仓库根目录执行：

```bash
uv venv
uv pip install -e ".[test]"
uv pip install -U "ksadk[all]"
cp .env.example .env
```

填写模型配置。默认本地知识库不需要云资源。

## 本地运行

```bash
cd 02-use-cases/knowledge-base-rag/adk
uv pip install -r requirements.txt
uv run agentengine run -i .
```

## Web UI 调试

```bash
uv run agentengine web .
```

Web UI 中可以连续询问部署、知识库和 KSADK 快速入门相关问题。

## 部署

```bash
uv run agentengine deploy .
```

部署前配置云账号 AK/SK。如果要使用云端知识库，还需要配置 `KSADK_KB_DATASET_ID`。

## 示例问题

```text
KSADK 怎么部署 Agent？
```

```text
当前知识库配置是什么？
```

## 可选云端知识库

在 `.env` 中填写：

```bash
KSADK_KB_DATASET_ID=your-dataset-id
KSADK_KB_ENDPOINT=aicp.api.ksyun.com
KSADK_KB_REGION=cn-beijing-6
KSADK_KB_SCHEME=https
```

未填写 dataset 时，示例会自动使用 `common/corpus/` 下的本地文档。

## 常见问题

- 如果没有云资源，保持 `KSADK_KB_DATASET_ID` 为空即可。
- 如果回答没有引用知识库内容，尝试明确询问 KSADK、部署或知识库相关问题。
- 如果云端检索失败，先用“当前知识库配置是什么？”检查 endpoint、region 和 dataset。
