# 部署指南

部署前需要准备可用的模型配置和金山云账号权限。常见环境变量包括 `OPENAI_API_KEY`、`OPENAI_API_BASE`、`OPENAI_MODEL_NAME`、`KSYUN_ACCESS_KEY` 和 `KSYUN_SECRET_KEY`。

每个样例目录都包含 `agentengine.yaml`。进入样例目录后，可以执行 `uv run agentengine deploy .` 发起部署。部署完成后，可以继续使用 AgentEngine 控制台或 CLI 调用 Agent。
