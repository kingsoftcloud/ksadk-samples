# 知识库模式

知识库 RAG 示例默认使用本地 corpus，因此 clone 仓库后不需要真实云知识库也能运行。

如果配置了 `KSADK_KB_DATASET_ID`，示例会切换到金山云知识库模式，并通过 `KSYUN_ACCESS_KEY`、`KSYUN_SECRET_KEY`、`KSADK_KB_ENDPOINT`、`KSADK_KB_REGION` 和 `KSADK_KB_SCHEME` 连接真实知识库服务。

